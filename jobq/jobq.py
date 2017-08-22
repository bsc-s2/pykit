import logging
import sys
import threading
import time
import types

from pykit import threadutil

if sys.version_info[0] == 2:
    import Queue
else:
    import queue as Queue

logger = logging.getLogger(__name__)


class EmptyRst(object):
    pass


class Finish(object):
    pass


class JobWorkerError(Exception):
    pass


class JobWorkerNotFound(JobWorkerError):
    pass


class JobManager(object):

    def __init__(self, workers, queue_size=1024, probe=None, keep_order=False):

        if probe is None:
            probe = {}

        self.workers = workers
        self.head_queue = _make_q(queue_size)
        self.probe = probe
        self.keep_order = keep_order

        self.sessions = []

        self.probe.update({
            'sessions': self.sessions,
            'probe_lock': threading.RLock(),
            'in': 0,
            'out': 0,
        })

        self.make_sessions()

    def make_sessions(self):

        inq = self.head_queue

        workers = self.workers + [_blackhole]
        for i, worker in enumerate(workers):

            if callable(worker):
                worker = (worker, 1)

            worker, n = worker

            sess = {'worker': worker,
                    'threads': {},
                    'input': inq,
                    'output': _make_q(),
                    'probe': self.probe,
                    'index': i,
                    'total': len(workers),
                    # When exiting, it is not allowed to change thread number.
                    # Because we need to send a `Finish` to each thread.
                    'exiting': False,
                    'running': True,
                    # left close, right open: 0 running, n not.
                    # Indicate what thread should have been running.
                    'running_index_range': [0, n],
                    # protect reading/writing session info
                    'session_lock': threading.RLock(),
                    }

            if self.keep_order:
                # to maximize concurrency
                sess['queue_of_outq'] = _make_q(n=1024 * 1024)

                # protect input.get() and ouput.put()
                sess['keep_order_lock'] = threading.RLock()
                sess['coordinator_thread'] = _make_worker_thread(
                    sess, _coordinate, sess['output'], 0)

            self.add_worker_thread(sess)

            self.sessions.append(sess)
            inq = sess['output']

    def add_worker_thread(self, sess):

        with sess['session_lock']:

            if sess['exiting']:
                logger.info('session exiting.'
                            ' Thread number change not allowed')
                return

            s, e = sess['running_index_range']

            for i in range(s, e):

                if i not in sess['threads']:

                    if self.keep_order:
                        th = _make_worker_thread(
                            sess, _exec_in_order, _make_q(), i)
                    else:
                        th = _make_worker_thread(
                            sess, _exec, sess['output'], i)

                    sess['threads'][i] = th

    def set_thread_num(self, worker, n):

        # When thread number is increased, new threads are created.
        # If thread number is reduced, we do not stop worker thread in this
        # function.
        # Because we do not have a steady way to shutdown a running thread in
        # python.
        # Worker thread checks if it should continue running in _exec() and
        # _exec_in_order(), by checking its thread_index against running thread
        # index range running_index_range.

        assert(n > 0)
        assert(isinstance(n, int))

        for sess in self.sessions:

            """
            In python2, `x = X(); x.meth is x.meth` results in a `False`.
            Every time to retrieve a method, python creates a new **bound** function.

            We must use == to test function equality.

            See https://stackoverflow.com/questions/15977808/why-dont-methods-have-reference-equality
            """

            if sess['worker'] != worker:
                continue

            with sess['session_lock']:

                if sess['exiting']:
                    logger.info('session exiting.'
                                ' Thread number change not allowed')
                    break

                s, e = sess['running_index_range']
                oldn = e - s

                if n < oldn:
                    s += oldn - n
                elif n > oldn:
                    e += n - oldn
                else:
                    break

                sess['running_index_range'] = [s, e]
                self.add_worker_thread(sess)

                logger.info('thread number is set to {n},'
                            ' thread index: {idx},'
                            ' running threads: {ths}'.format(
                                n=n,
                                idx=range(sess['running_index_range'][0],
                                          sess['running_index_range'][1]),
                                ths=sorted(sess['threads'].keys())))
                break

        else:
            raise JobWorkerNotFound(worker)

    def put(self, elt):
        self.head_queue.put(elt)

    def join(self, timeout=None):

        endtime = time.time() + (timeout or 86400 * 365)

        for sess in self.sessions:

            with sess['session_lock']:
                # prevent adding or removing thread
                sess['exiting'] = True
                ths = sess['threads'].values()

            # put nr = len(threads) Finish
            for th in ths:
                sess['input'].put(Finish)

            for th in ths:
                th.join(endtime - time.time())

            if 'queue_of_outq' in sess:
                sess['queue_of_outq'].put(Finish)
                sess['coordinator_thread'].join(endtime - time.time())

            # if join timeout, let threads quit at next loop
            sess['running'] = False

    def stat(self):
        return stat(self.probe)


def run(input_it, workers, keep_order=False, timeout=None, probe=None):

    mgr = JobManager(workers, probe=probe, keep_order=keep_order)

    for args in input_it:
        mgr.put(args)

    mgr.join(timeout=timeout)


def stat(probe):

    with probe['probe_lock']:
        rst = {
            'in': probe['in'],
            'out': probe['out'],
            'doing': probe['in'] - probe['out'],
            'workers': [],
        }

    # exclude the _start and _end
    for sess in probe['sessions'][:-1]:
        o = {}
        wk = sess['worker']
        o['name'] = (wk.__module__ or 'builtin') + ":" + wk.__name__
        o['input'] = _q_stat(sess['input'])
        if 'queue_of_outq' in sess:
            o['coordinator'] = _q_stat(sess['queue_of_outq'])

        s, e = sess['running_index_range']
        o['nr_worker'] = e - s

        rst['workers'].append(o)

    return rst


def _q_stat(q):
    return {'size': q.qsize(),
            'capa': q.maxsize
            }


def _exec(sess, output_q, thread_index):

    while sess['running']:

        # If this thread is not in the running thread range, exit.
        if thread_index < sess['running_index_range'][0]:

            with sess['session_lock']:
                del sess['threads'][thread_index]

            logger.info('worker-thread {i} quit'.format(i=thread_index))
            return

        args = sess['input'].get()
        if args is Finish:
            return

        with sess['probe']['probe_lock']:
            sess['probe']['in'] += 1

        try:
            rst = sess['worker'](args)
        except Exception as e:
            logger.exception(repr(e))
            continue

        finally:
            with sess['probe']['probe_lock']:
                sess['probe']['out'] += 1

        # If rst is an iterator, it procures more than one args to next job.
        # In order to be accurate, we only count an iterator as one.

        _put_rst(output_q, rst)


def _exec_in_order(sess, output_q, thread_index):

    while sess['running']:

        if thread_index < sess['running_index_range'][0]:

            with sess['session_lock']:
                del sess['threads'][thread_index]

            logger.info('in-order worker-thread {i} quit'.format(
                i=thread_index))
            return

        with sess['keep_order_lock']:

            args = sess['input'].get()
            if args is Finish:
                return
            sess['queue_of_outq'].put(output_q)

        with sess['probe']['probe_lock']:
            sess['probe']['in'] += 1

        try:
            rst = sess['worker'](args)

        except Exception as e:
            logger.exception(repr(e))
            output_q.put(EmptyRst)
            continue

        finally:
            with sess['probe']['probe_lock']:
                sess['probe']['out'] += 1

        output_q.put(rst)


def _coordinate(sess, output_q, thread_index):

    while sess['running']:

        outq = sess['queue_of_outq'].get()
        if outq is Finish:
            return

        _put_rst(output_q, outq.get())


def _put_rst(output_q, rst):

    if type(rst) == types.GeneratorType:
        for rr in rst:
            _put_non_empty(output_q, rr)
    else:
        _put_non_empty(output_q, rst)


def _blackhole(args):
    return EmptyRst


def _put_non_empty(q, val):
    if val is not EmptyRst:
        q.put(val)


def _make_q(n=1024):
    return Queue.Queue(n)


def _make_worker_thread(sess, exec_func, outq, thread_index):
    # `thread_index` identifying a thread in sess['threads'].
    # It is used to decide which thread to remove.
    return threadutil.start_daemon_thread(exec_func,
                                          args=(sess, outq, thread_index,))
