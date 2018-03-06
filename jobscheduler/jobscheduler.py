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

RUNNING = 'running'
FINISHED = 'finished'
FAILED = 'failed'
ABORTED = 'aborted'
INACTIVE = 'inactive'

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

    def __init__(self, jobs, dump_status=None, reload_status=None, filter_job=None):
        self.lock = threading.RLock()
        self.jobs = jobs
        self.job_status = {}
        self.job_threads = {}
        self.dump_status = dump_status
        self.reload_status = reload_status
        self.filter_job = filter_job

        if self.reload_status is not None:
            try:
                job_status = self.reload_status()
                logger.info('loaded job_status: %s', repr(job_status))

                if job_status is not None:
                    self.job_status = job_status

            except Exception as e:
                logger.exception('failed to reload job status: %s' % repr(e))

    def run_job(self, curr_time, job_name, job_conf, status):
        libc = ctypes.cdll.LoadLibrary('libc.so.6')
        tid = libc.syscall(SYS_gettid)

        with self.lock:
            status['start_time'] = curr_time
            status['stat'] = RUNNING
            status['thread_id'] = tid
            status['message'] = ''

        try:
            job_conf['func'](*job_conf['args'], **job_conf['kwargs'])

            with self.lock:
                status['finish_time'] = get_time_info(ts=time.time())
                status['stat'] = FINISHED

        except Exception as e:
            logger.exception('failed to run job: %s, %s' %
                             (job_name, repr(e)))

            with self.lock:
                status['fail_time'] = get_time_info(ts=time.time())
                status['stat'] = FAILED
                status['message'] = repr(e)

    def fire(self, curr_time, job_name, job_conf, status):
        th = self.job_threads.get(job_name)

        if th is not None and th.is_alive():
            return

        self.job_threads[job_name] = threadutil.start_daemon_thread(
            self.run_job, args=(curr_time, job_name, job_conf, status))

    def schedule_one_job(self, curr_time, job_name, job_conf):
        if job_name not in self.job_status:
            self.job_status[job_name] = {}

        status = self.job_status[job_name]

        status['curr_time'] = curr_time

        if self.filter_job is not None:
            need_run = self.filter_job(job_conf)

            if not need_run:
                status['stat'] = INACTIVE
                status['message'] = 'this job do not need to run'
                return

        if 'next_fire_time' not in status:
            if job_conf.get('at') is None:
                status['fire_time'] = curr_time

                self.fire(curr_time, job_name, job_conf, status)

                status['next_fire_time'] = get_next_fire_time(
                    job_conf, status['fire_time']['ts'])

            else:
                n, unit = job_conf['every']
                interval = n * SECOND[unit]

                next_fire_time = get_next_fire_time(
                    job_conf, curr_time['ts'] - interval)

                if next_fire_time['ts'] < curr_time['ts']:
                    next_fire_time = get_next_fire_time(
                        job_conf, curr_time['ts'])

                status['next_fire_time'] = next_fire_time

        if curr_time['ts'] >= status['next_fire_time']['ts']:
            status['fire_time'] = curr_time

            self.fire(curr_time, job_name, job_conf, status)

            status['next_fire_time'] = get_next_fire_time(
                job_conf, status['fire_time']['ts'])

    def _schedule(self, curr_time):
        for job_name, job_conf in self.jobs.iteritems():
            try:
                self.schedule_one_job(curr_time, job_name, job_conf)

            except Exception as e:
                logger.exception('failed to schedule job: %s, %s'
                                 % (job_name, repr(e)))

    def schedule(self):
        for job_name, status in self.job_status.items():
            if job_name not in self.jobs:
                del(self.job_status[job_name])
                continue

            if status.get('stat') == RUNNING:
                self.job_status[job_name]['stat'] = ABORTED
                self.job_status[job_name]['message'] = 'aborted by restart'

        while True:
            curr_time = get_time_info(time.time())

            with self.lock:
                self._schedule(curr_time)

            if self.dump_status is not None:
                try:
                    self.dump_status(self.job_status)
                except Exception as e:
                    logger.exception('failed to dump job status: %s' % repr(e))

            logger.info('job status: %s' % utfjson.dump(self.job_status))

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

            if job_name in self.job_status:
                del(self.job_status[job_name])

            if job_name in self.job_threads:
                del(self.job_threads[job_name])
