import ctypes
import datetime
import logging
import threading
import time

import pytz
import tzlocal

from pykit import threadutil
from pykit import timeutil
from pykit import utfjson

SYS_gettid = 186

logger = logging.getLogger(__name__)


class NextFireTimeError(Exception):
    pass


class JobExistError(Exception):
    pass


SECOND = {
    'second': 1,
    'minute': 60,
    'hour': 60 * 60,
    'day': 60 * 60 * 24,
    'week': 60 * 60 * 24 * 7,
    'month': 60 * 60 * 24 * 31,
}


def get_time_info(ts=None, tz=None):
    if ts is None:
        ts = time.time()

    if tz is None:
        tz = tzlocal.get_localzone()

    dt = datetime.datetime.fromtimestamp(ts, tz)

    time_info = {
        'ts': ts,
        'string': str(dt),
    }

    return time_info


def get_next_fire_time(conf, last_fire_ts):
    n, unit = conf['every']
    interval = n * SECOND[unit]

    next_ts = last_fire_ts + interval

    at = conf.get('at')

    if at is None:
        return get_time_info(next_ts)

    timezone_name = conf.get('timezone')

    if timezone_name is None:
        tz = tzlocal.get_localzone()
    else:
        tz = pytz.timezone(timezone_name)

    next_dt = datetime.datetime.fromtimestamp(next_ts, tz)
    actual_next_dt = next_dt.replace(**at)

    actual_next_ts = timeutil.datetime_to_ts(actual_next_dt)

    next_fire_time = get_time_info(actual_next_ts)

    if actual_next_ts <= last_fire_ts:
        msg = ('next fire time: %s, is before last fire ts: %f, conf: %s' %
               (repr(next_fire_time), last_fire_ts, repr(conf)))
        raise NextFireTimeError(msg)

    return next_fire_time


class JobScheduler(object):

    def __init__(self, jobs, dump_status=None, reload_status=None,
                 should_job_run=None):
        self.lock = threading.RLock()
        self.jobs = jobs
        self.status = {}

        self.dump_status = dump_status
        self.reload_status = reload_status
        self.should_job_run = should_job_run

        if self.reload_status is not None:
            try:
                status = self.reload_status()
                logger.info('loaded job_status: %s', repr(status))

                if status is not None:
                    self.status = status

            except Exception as e:
                logger.exception('failed to reload job status: %s' % repr(e))

    def append_log(self, job_status, job_conf, log_msg):
        job_status['log'].append(log_msg)

        # log at start and end, add keep 3 more entries.
        n = job_conf['concurrence_n'] * 2 + 3
        job_status['log'] = job_status['log'][-n:]

    def run_job(self, curr_time, job_name, job_conf, job_status):
        thread_id = None
        thread_ident = threading.current_thread().ident

        try:
            libc = ctypes.cdll.LoadLibrary('libc.so.6')
            thread_id = libc.syscall(SYS_gettid)
        except Exception as e:
            logger.info('failed to get thread id: %s' + repr(e))

        with self.lock:
            job_status['active_threads'][thread_ident] = {
                'start_time': curr_time,
                'thread_ident': thread_ident,
                'thread_id': thread_id,
            }

            log_msg = 'thread: %s-%s started at: %s' % (
                thread_ident, thread_id, curr_time)
            self.append_log(job_status, job_conf, log_msg)

        try:
            job_conf['func'](*job_conf['args'], **job_conf['kwargs'])

            with self.lock:
                log_msg = 'thread: %s-%s finished at: %s' % (
                    thread_ident, thread_id, get_time_info(ts=time.time()))
                self.append_log(job_status, job_conf, log_msg)

                del(job_status['active_threads'][thread_ident])

        except Exception as e:
            logger.exception('failed to run job: %s, %s' %
                             (job_name, repr(e)))

            with self.lock:
                log_msg = 'thread: %s-%s failed at: %s' % (
                    thread_ident, thread_id, get_time_info(ts=time.time()))
                self.append_log(job_status, job_conf, log_msg)

                del(job_status['active_threads'][thread_ident])
                job_status['message'] = repr(e)

    def fire(self, curr_time, job_name, job_conf, job_status):
        thread_n = len(job_status['active_threads'])

        if thread_n >= job_conf['concurrence_n']:
            log_msg = 'at time: %s, already have %d threads for job: %s' % (
                curr_time, thread_n, job_name)
            self.append_log(job_status, job_conf, log_msg)

            logger.error('too many threads for job: %s' % job_name)
            return

        logger.info('at time: %s, start to run job: %s' %
                    (curr_time, job_name))

        threadutil.start_daemon_thread(
            self.run_job, args=(curr_time, job_name, job_conf, job_status))

        job_status['message'] = ''

    def schedule_one_job(self, curr_time, job_name, job_conf):
        if 'concurrence_n' not in job_conf:
            job_conf['concurrence_n'] = 1

        if job_name not in self.status:
            self.status[job_name] = {
                'active_threads': {},
                'log': [],
            }

        job_status = self.status[job_name]

        job_status['curr_time'] = curr_time

        if self.should_job_run is not None:
            should_run = self.should_job_run(job_conf)

            if not should_run:
                job_status['message'] = 'this job do not need to run'
                return

        if 'next_fire_time' not in job_status:
            if job_conf.get('at') is None:
                job_status['fire_time'] = curr_time

                self.fire(curr_time, job_name, job_conf, job_status)

                job_status['next_fire_time'] = get_next_fire_time(
                    job_conf, curr_time['ts'])

            else:
                n, unit = job_conf['every']
                interval = n * SECOND[unit]

                next_fire_time = get_next_fire_time(
                    job_conf, curr_time['ts'] - interval)

                if next_fire_time['ts'] < curr_time['ts']:
                    next_fire_time = get_next_fire_time(
                        job_conf, curr_time['ts'])

                job_status['next_fire_time'] = next_fire_time

        if curr_time['ts'] >= job_status['next_fire_time']['ts']:
            job_status['fire_time'] = curr_time

            self.fire(curr_time, job_name, job_conf, job_status)

            job_status['next_fire_time'] = get_next_fire_time(
                job_conf, job_status['next_fire_time']['ts'])

    def _schedule(self, curr_time):
        for job_name, job_conf in self.jobs.iteritems():
            try:
                self.schedule_one_job(curr_time, job_name, job_conf)

            except Exception as e:
                logger.exception('failed to schedule job %s: %s' %
                                 (job_name, repr(e)))

    def schedule(self):
        for job_name, job_status in self.status.items():
            if job_name not in self.jobs:
                del(self.status[job_name])
                continue

            if len(job_status['active_threads']) > 0:
                msg = 'threads aborted by restart: %s' % (
                    job_status['active_threads'])
                self.status[job_name]['message'] = msg
                self.status[job_name]['active_threads'] = {}

        while True:
            curr_time = get_time_info(time.time())

            with self.lock:
                self._schedule(curr_time)

            if self.dump_status is not None:
                try:
                    self.dump_status(self.status)
                except Exception as e:
                    logger.exception('failed to dump job status: %s' % repr(e))

            for job_name, job_status in self.status.items():
                logger.info('status of job %s, %s' %
                            (job_name, utfjson.dump(job_status)))

            end_time = time.time()

            logger.info('scheduled at: %s, time used: %f' %
                        (repr(curr_time), end_time - curr_time['ts']))

            to_sleep = 60 - (end_time % 60) + 1
            time.sleep(to_sleep)

    def add_job(self, job_name, job_conf):
        with self.lock:
            if job_name in self.jobs:
                raise JobExistError('job: %s already exists' % job_name)

            self.jobs[job_name] = job_conf

    def delete_job(self, job_name):
        with self.lock:
            if job_name in self.jobs:
                del(self.jobs[job_name])

            if job_name in self.status:
                del(self.status[job_name])
