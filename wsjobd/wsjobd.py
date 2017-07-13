#!/usr/bin/env python2
# coding: utf-8

import logging
import threading
import time

import psutil
from geventwebsocket import WebSocketApplication, WebSocketError

from pykit import utfjson

logger = logging.getLogger(__name__)

MEM_LOW_THRESHOLD = 500 * 1024 ** 2  # 500M
CPU_LOW_THRESHOLD = 3  # 3%
MAX_CLIENT_NUMBER = 1000
JOBS_DIR = 'jobs'


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

        with self.lock:
            if self.ident in self.sessions:
                logger.info('job: %s already exists, created by chennel %s' %
                            (self.ident, repr(self.sessions[self.ident].channel)))
                return
            else:
                self.sessions[self.ident] = self
                logger.info(('inserted job: %s to sessions by channel %s, ' +
                             'there are %d jobs in sessions now') %
                            (self.ident, repr(self.channel), len(self.sessions)))

        self.thread = make_thread(self.work, ())

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
    Job(channel, msg, func)

    # job might just finished and is removed
    job = Job.sessions.get(msg['ident'])

    return job


def make_thread(target, args):
    th = threading.Thread(target=target, args=args)
    th.daemon = True
    th.start()
    return th


def progress_sender(job, channel, interval=5, stat=None):

    stat = stat or (lambda data: data)
    data = job.data

    i = 10
    try:
        while True:
            # if thread died due to some reason, still send 10 stats
            if not job.thread.is_alive():
                logger.info('job %s died: %s' % (job.ident, repr(job.err)))
                i -= 1
                if i == 0:
                    channel.ws.close()
                    break

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

    def on_open(self):
        logger.info('on open, the channel is: ' + repr(self))
        self.ignore_message = False

    def on_message(self, message):
        logger.info('on message, the channel is: %s, the message is: %s' %
                    (repr(self), message))

        try:
            if self.ignore_message == True:
                return

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

            self._setup_response(msg)
            self.ignore_message = True
            return

        except SystemOverloadError as e:
            logger.info('system overload on chennel %s, %s'
                        % (repr(self), repr(e)))
            self._send_err(e)
            time.sleep(3)
            self.ws.close()

        except JobError as e:
            logger.info('error on channel %s while handling message, %s'
                        % (repr(self), repr(e)))
            self._send_err(e)
            time.sleep(3)
            self.ws.close()

        except Exception as e:
            logger.exception(('exception on channel %s while handling ' +
                              'message, %s') % (repr(self), repr(e)))
            self._send_err(e)
            time.sleep(3)
            self.ws.close()

    def _send_err(self, err):
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
            'mem_available': psutil.virtual_memory().available,
            'cpu_idle_percent': psutil.cpu_times_percent(
                self.cpu_sample_interval).idle,
            'client_number': len(self.protocol.server.clients),
        }

    def _check_system_load(self, check_load):
        mem_low_threshold = check_load.get('mem_low_threshold',
                                           MEM_LOW_THRESHOLD)
        cpu_low_threshold = check_load.get('cpu_low_threshold',
                                           CPU_LOW_THRESHOLD)
        max_client_number = check_load.get('max_client_number',
                                           MAX_CLIENT_NUMBER)

        if not isinstance(mem_low_threshold, (int, long, float)):
            raise InvalidMessageError('mem_low_threshold is not a number')

        if not isinstance(cpu_low_threshold, (int, long, float)):
            raise InvalidMessageError('cpu_low_threshold is not a number')

        if not isinstance(max_client_number, (int, long, float)):
            raise InvalidMessageError('max_client_number is not a number')

        system_load = self.get_system_load()

        if system_load['mem_available'] < mem_low_threshold:
            raise SystemOverloadError(
                'available memory: %d is less than: %d' %
                (system_load['mem_available'], mem_low_threshold))

        if system_load['cpu_idle_percent'] < cpu_low_threshold:
            raise SystemOverloadError(
                'cpu idle percent: %f is lower than: %f' %
                (system_load['cpu_idle_percent'], cpu_low_threshold))

        if system_load['client_number'] > max_client_number:
            raise SystemOverloadError(
                'client number: %d is larger than: %d' %
                (system_load['client_number'], max_client_number))

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

        make_thread(target=progress_sender, args=(job, channel, interval, lam))

    def _get_func_by_name(self, msg):

        mod_func = msg['func'].split('.')
        mod_name = '.'.join(mod_func[:-1])
        func_name = mod_func[-1]

        try:
            mod = __import__('%s.%s' % (JOBS_DIR, mod_name))
        except (ImportError, SyntaxError) as e:
            raise LoadingError('failed to import %s: %s' % (mod_name, repr(e)))

        mod = getattr(mod, mod_name)
        logger.info('mod imported from: ' + repr(mod.__file__))

        try:
            func = getattr(mod, func_name)
        except AttributeError as e:
            raise LoadingError("function not found: " + repr(func_name))

        return func

    def on_close(self, reason):
        logger.info('on close, the channel is: ' + repr(self))
