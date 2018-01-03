#!/usr/bin/env python2
# coding: utf-8

import logging
import threading
import time
from collections import OrderedDict

import psutil
from geventwebsocket import Resource
from geventwebsocket import WebSocketApplication
from geventwebsocket import WebSocketError
from geventwebsocket import WebSocketServer

from pykit import threadutil
from pykit import utfjson
from pykit import jobq

logger = logging.getLogger(__name__)

MEM_AVAILABLE = 'mem_available'
CPU_IDLE_PERCENT = 'cpu_idle_percent'
CLIENT_NUMBER = 'client_number'
JOBS_DIR = 'jobs'

CHECK_LOAD_PARAMS = {
    'mem_low_threshold': {
        'load_name': MEM_AVAILABLE,
        'default': 500 * 1024 ** 2,  # 500M
        'greater': True,
    },
    'cpu_low_threshold': {
        'load_name': CPU_IDLE_PERCENT,
        'default': 3,  # 3%
        'greater': True,
    },
    'max_client_number': {
        'load_name': CLIENT_NUMBER,
        'default': 1000,
        'greater': False,
    },
}


class SystemOverloadError(Exception):
    pass


class JobError(Exception):
    pass


class InvalidMessageError(JobError):
    pass


class InvalidProgressError(InvalidMessageError):
    pass


class LoadingError(JobError):
    pass


class JobNotInSessionError(JobError):
    pass


class Job(object):

    lock = threading.RLock()
    sessions = {}

    def __init__(self, channel, msg, func):

        self.ident = msg['ident']
        self.channel = channel
        self.data = msg
        self.worker = func
        self.ctx = {}
        self.err = None

        if self.ident in self.sessions:
            logger.info('job: %s already exists, created by chennel %s' %
                        (self.ident, repr(self.sessions[self.ident].channel)))
            return
        else:
            self.sessions[self.ident] = self
            logger.info(('inserted job: %s to sessions by channel %s, ' +
                         'there are %d jobs in sessions now') %
                        (self.ident, repr(self.channel), len(self.sessions)))

        self.thread = threadutil.start_thread(target=self.work, args=(),
                                              daemon=True)

    def work(self):

        logger.info("job %s started, the data is: %s" %
                    (self.ident, self.data))

        try:
            self.worker(self)
        except Exception as e:
            logger.exception('job %s got exception: %s' %
                             (self.ident, repr(e)))
            self.err = e
        finally:
            logger.info('job %s ended' % self.ident)
            self.close()

    def close(self):

        with self.lock:
            del self.sessions[self.ident]
            logger.info(('removed job: %s from sessions, there are %d ' +
                         'jobs in sessions now') %
                        (self.ident, len(self.sessions)))


def get_or_create_job(channel, msg, func):

    with Job.lock:
        Job(channel, msg, func)

        job = Job.sessions.get(msg['ident'])

    return job


def progress_sender(job, channel, interval=5, stat=None):

    stat = stat or (lambda data: data)
    data = job.data

    i = 10
    try:
        while True:
            # if thread died due to some reason, still send 10 stats
            if not job.thread.is_alive():
                logger.info('job %s died: %s' % (job.ident, repr(job.err)))
                if i == 0:
                    channel.ws.close()
                    break
                i -= 1

            logger.info('jod %s on channel %s send progress: %s' %
                        (job.ident, repr(channel), repr(stat(data))))

            to_send = stat(data)
            if channel.report_system_load and type(to_send) == type({}):
                to_send['system_load'] = channel.get_system_load()

            channel.ws.send(utfjson.dump(to_send))

            time.sleep(interval)

    except WebSocketError as e:
        if channel.ws.closed == True:
            logger.info('the client has closed the connection')
        else:
            logger.exception(('got websocket error when sending progress on' +
                              ' channel %s: %s') % (repr(channel), repr(e)))

    except Exception as e:
        logger.exception('got exception when sending progress on channel %s: %s'
                         % (repr(channel), repr(e)))
        channel.ws.close()


class JobdWebSocketApplication(WebSocketApplication):

    jobq_mgr = None

    def on_open(self):
        logger.info('on open, the channel is: ' + repr(self))
        self.ignore_message = False

    def _parse_request(self, message):
        try:
            try:
                msg = utfjson.load(message)
            except Exception as e:
                raise InvalidMessageError(
                    'message is not a vaild json string: %s' % message)

            self._check_msg(msg)

            self.report_system_load = msg.get('report_system_load') == True
            self.cpu_sample_interval = msg.get('cpu_sample_interval', 0.02)

            if not isinstance(self.cpu_sample_interval, (int, long, float)):
                raise InvalidMessageError(
                    'cpu_sample_interval is not a number')

            check_load = msg.get('check_load')
            if type(check_load) == type({}):
                self._check_system_load(check_load)

            self.jobs_dir = msg.get('jobs_dir', JOBS_DIR)

            self._setup_response(msg)
            return

        except SystemOverloadError as e:
            logger.info('system overload on chennel %s, %s'
                        % (repr(self), repr(e)))
            self._send_err_and_close(e)

        except JobError as e:
            logger.info('error on channel %s while handling message, %s'
                        % (repr(self), repr(e)))
            self._send_err_and_close(e)

        except Exception as e:
            logger.exception(('exception on channel %s while handling ' +
                              'message, %s') % (repr(self), repr(e)))
            self._send_err_and_close(e)

    def on_message(self, message):
        logger.info('on message, the channel is: %s, the message is: %s' %
                    (repr(self), message))
        if self.ignore_message:
            return

        else:
            self.ignore_message = True

        self.jobq_mgr.put((self, message))

    def _send_err_and_close(self, err):
        try:
            err_msg = {
                'err': err.__class__.__name__,
                'val': err.args,
            }
            self.ws.send(utfjson.dump(err_msg))
        except Exception as e:
            logger.error(('error on channel %s while sending back error '
                          + 'message, %s') % (repr(self), repr(e)))

    def get_system_load(self):
        return {
            MEM_AVAILABLE: psutil.virtual_memory().available,
            CPU_IDLE_PERCENT: psutil.cpu_times_percent(
                self.cpu_sample_interval).idle,
            CLIENT_NUMBER: len(self.protocol.server.clients),
        }

    def _check_system_load(self, check_load):
        system_load = self.get_system_load()

        for param_name, param_attr in CHECK_LOAD_PARAMS.iteritems():
            param_value = check_load.get(param_name, param_attr['default'])

            if not isinstance(param_value, (int, long, float)):
                raise InvalidMessageError('%s is not a number' % param_name)

            load_name = param_attr['load_name']
            diff = system_load[load_name] - param_value

            if not param_attr['greater']:
                diff = 0 - diff

            if diff < 0:
                raise SystemOverloadError(
                    '%s: %d is %s than: %d' %
                    (load_name, system_load[load_name],
                     param_attr['greater'] and 'less' or 'greater',
                     param_value))

    def _check_msg(self, msg):
        if type(msg) != type({}):
            raise InvalidMessageError("message is not dictionary")

        if 'ident' not in msg:
            raise InvalidMessageError("'ident' is not in message")

        if 'func' not in msg:
            raise InvalidMessageError("'func' is not in message")

    def _setup_response(self, msg):

        func = self._get_func_by_name(msg)
        channel = self
        job = get_or_create_job(channel, msg, func)

        if job is None:
            raise JobNotInSessionError(
                'job not in sessions: ' + repr(Job.sessions))

        progress = msg.get('progress', {})

        if progress in (None, False):
            return

        if type(progress) != type({}):
            raise InvalidProgressError(
                'the progress in message is not a dictionary')

        interval = progress.get('interval', 5)
        progress_key = progress.get('key')

        if progress_key is None:
            lam = lambda r: r
        else:
            lam = lambda r: r[progress_key]

        threadutil.start_thread(target=progress_sender,
                                args=(job, channel, interval, lam),
                                daemon=True)

    def _get_func_by_name(self, msg):
        mod_func = self.jobs_dir.split('/') + msg['func'].split('.')
        mod_path = '.'.join(mod_func[:-1])
        func_name = mod_func[-1]

        try:
            mod = __import__(mod_path)
        except (ImportError, SyntaxError) as e:
            raise LoadingError('failed to import %s: %s' % (mod_path, repr(e)))

        for mod_name in mod_path.split('.')[1:]:
            mod = getattr(mod, mod_name)

        logger.info('mod imported from: ' + repr(mod.__file__))

        try:
            func = getattr(mod, func_name)
        except AttributeError as e:
            raise LoadingError("function not found: " + repr(func_name))

        return func

    def on_close(self, reason):
        logger.info('on close, the channel is: ' + repr(self))


def _parse_request(args):
    app, msg = args
    app._parse_request(msg)


def run(ip='127.0.0.1', port=63482, jobq_thread_count=10):
    JobdWebSocketApplication.jobq_mgr = jobq.JobManager(
        [(_parse_request, jobq_thread_count)])

    WebSocketServer(
        (ip, port),
        Resource(OrderedDict({'/': JobdWebSocketApplication})),
    ).serve_forever()
