import logging
import sys
import threading
import time
import types

if sys.version_info[0] == 2:
    import Queue
else:
    import queue as Queue

logger = logging.getLogger(__name__)


class EmptyRst(object):
    pass


class Finish(object):
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
        keep_order = self.keep_order

        workers = self.workers + [_blackhole]
        for i, worker in enumerate(workers):

            if callable(worker):
                worker = (worker, 1)

            worker, n = worker

            sess = {'worker': worker,
                    'threads': [],
                    'input': inq,
                    'probe': self.probe,
                    'index': i,
                    'total': len(workers),
                    'running': True,
                    }

            outq = _make_q()

            if keep_order and n > 1:
                # to maximize concurrency
                sess['queue_of_outq'] = _make_q(n=1024 * 1024)
                sess['lock'] = threading.RLock()
                sess['coor_th'] = _thread(_coordinate, (sess, outq))

                sess['threads'] = [_thread(_exec_in_order, (sess, _make_q()))
                                   for ii in range(n)]
            else:
                sess['threads'] = [_thread(_exec, (sess, outq))
                                   for ii in range(n)]

            self.sessions.append(sess)
            inq = outq

    def put(self, elt):
        self.head_queue.put(elt)

    def join(self, timeout=None):

        endtime = time.time() + (timeout or 86400 * 365)

        for sess in self.sessions:

            # put nr = len(threads) Finish
            for th in sess['threads']:
                sess['input'].put(Finish)

            for th in sess['threads']:
                th.join(endtime - time.time())

            if 'queue_of_outq' in sess:
                sess['queue_of_outq'].put(Finish)
                sess['coor_th'].join(endtime - time.time())

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
        o['name'] = wk.__module__ + ":" + wk.__name__

        o['input'] = _q_stat(sess['input'])
        if 'queue_of_outq' in sess:
            o['coordinator'] = _q_stat(sess['queue_of_outq'])

        rst['workers'].append(o)

    return rst


def _q_stat(q):
    return {'size': q.qsize(),
            'capa': q.maxsize
            }


def _exec(sess, output_q):

    while sess['running']:

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


def _exec_in_order(sess, output_q):

    while sess['running']:

        with sess['lock']:

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


def _coordinate(sess, output_q):

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


def _thread(func, args):
    th = threading.Thread(target=func,
                          args=args)
    th.daemon = True
    th.start()

    return th
