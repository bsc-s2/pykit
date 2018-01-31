import logging
import random
import threading
import time
import unittest

from pykit import jobq
from pykit import threadutil
from pykit import ututil

dd = ututil.dd


def add1(args):
    return args + 1


def multi2(args):
    return args * 2


def multi2_sleep(args):
    time.sleep(0.02)
    return args * 2


def discard_even(args):
    if args % 2 == 0:
        return jobq.EmptyRst
    else:
        return args


def sleep_5(args):
    time.sleep(5)
    return args


class TestProbe(unittest.TestCase):

    def _start_jobq_in_thread(self, n_items, n_worker, keep_order=False):

        def _sleep_1(args):
            time.sleep(0.1)
            return args

        def _nothing(args):
            return args

        probe = {}
        th = threading.Thread(target=lambda: jobq.run(range(n_items),
                                                      [(_sleep_1, n_worker),
                                                       _nothing],
                                                      probe=probe,
                                                      keep_order=keep_order,
                                                      ))
        th.daemon = True
        th.start()

        return th, probe

    def test_probe_single_thread(self):

        cases = (
                (0.05, 1, '_sleep_1 is working on 1st'),
                (0.1,  1, '_sleep_1 is working on 2nd'),
                (0.2,  0, 'all done'),
        )

        th, probe = self._start_jobq_in_thread(3, 1)

        for sleep_time, doing, case_mes in cases:

            time.sleep(sleep_time)
            stat = jobq.stat(probe)

            self.assertEqual(doing, stat['doing'], case_mes)

            # qsize() is not reliable. do not test the value of it.
            self.assertTrue(stat['workers'][0]['input']['size'] >= 0)
            self.assertTrue(stat['workers'][0]['input']['capa'] >= 0)

        # use the last stat

        workers = stat['workers']
        self.assertEqual(2, len(workers))

        w0 = workers[0]
        self.assertEqual(True, w0['name'].endswith(':_sleep_1'))
        self.assertEqual(0,    w0['input']['size'])
        self.assertEqual(True, w0['input']['capa'] > 0)

        th.join()

    def test_probe_3_thread(self):

        cases = (
                (0.05, 3, '_sleep_1 is working on 1st 3 items'),
                (0.1,  3, '_sleep_1 is working on 2nd 3 items'),
                (0.4,  0, 'all done'),
        )

        th, probe = self._start_jobq_in_thread(10, 3)

        for sleep_time, doing, case_mes in cases:

            time.sleep(sleep_time)
            stat = jobq.stat(probe)

            self.assertEqual(doing, stat['doing'], case_mes)

        # use the last stat

        workers = stat['workers']
        self.assertEqual(2, len(workers))

        th.join()

    def test_probe_3_thread_keep_order(self):

        cases = (
                (0.05, 3, '_sleep_1 is working on 1st 3 items'),
                (0.1,  3, '_sleep_1 is working on 2nd 3 items'),
                (0.4,  0, 'all done'),
        )

        th, probe = self._start_jobq_in_thread(10, 3, keep_order=True)

        for sleep_time, doing, case_mes in cases:

            time.sleep(sleep_time)
            stat = jobq.stat(probe)

            self.assertEqual(doing, stat['doing'], case_mes)

        # use the last stat

        workers = stat['workers']
        self.assertEqual(2, len(workers))

        th.join()


class TestDispatcher(unittest.TestCase):

    def test_dispatcher_job_manager(self):

        n_threads = 3
        n_numbers = 1000
        rst = {}
        ordered = []

        def _collect_by_tid(ii):

            tid = threading.current_thread().ident
            if tid not in rst:
                rst[tid] = []

            rst[tid].append(ii)
            return ii

        def _collect(ii):
            ordered.append(ii)

        jm = jobq.JobManager([
            (_collect_by_tid, n_threads, lambda x: x % n_threads),
            (_collect, 1),
        ])

        # In dispatcher mode it does not allow to set thread_num to prevent out
        # of order output
        self.assertRaises(jobq.JobWorkerError, jm.set_thread_num, _collect_by_tid, 10)

        for i in range(n_numbers):
            jm.put(i)

            st = jm.stat()
            dd(st)

            self.assertIn('dispatcher', st['workers'][0])
            dstat = st['workers'][0]['dispatcher']
            self.assertEqual(n_threads, len(dstat))
            for ds in dstat:
                self.assertIn('input', ds)
                self.assertIn('output', ds)

        jm.join()

        self.assertEqual(n_threads, len(rst.keys()))

        for arr in rst.values():
            m = arr[0] % n_threads
            for i in arr:
                # a thread receives args with the same mod by `n_threads`
                self.assertEqual(m, i % n_threads)

        # with dispatcher, output are ordered
        self.assertEqual([x for x in range(n_numbers)],
                         ordered)

    def test_dispatcher_run(self):

        n_threads = 3
        n_numbers = 1000
        rst = {}
        ordered = []

        def _collect_by_tid(ii):

            tid = threading.current_thread().ident
            if tid not in rst:
                rst[tid] = []

            rst[tid].append(ii)
            return ii

        def _collect(ii):
            ordered.append(ii)

        jobq.run(range(n_numbers), [
            (_collect_by_tid, n_threads, lambda x: x % n_threads),
            (_collect, 1),
        ])

        self.assertEqual(n_threads, len(rst.keys()))

        for arr in rst.values():
            m = arr[0] % n_threads
            for i in arr:
                # a thread receives args with the same mod by `n_threads`
                self.assertEqual(m, i % n_threads)

        # with dispatcher, output are ordered
        self.assertEqual([x for x in range(n_numbers)],
                         ordered)


class TestTimeout(unittest.TestCase):

    def test_timeout(self):

        def _sleep_1(args):
            sleep_got.append(args)
            time.sleep(0.1)
            return args

        def collect(args):
            rst.append(args)

        # collect quits before it get any item from its input queue

        rst = []
        sleep_got = []
        jobq.run(range(10), [_sleep_1, collect], timeout=0.05)
        time.sleep(0.2)
        self.assertEqual([0], sleep_got)
        self.assertEqual([], rst)

        rst = []
        sleep_got = []
        jobq.run(range(10), [_sleep_1, collect], timeout=0.15)
        time.sleep(0.2)
        self.assertEqual([0, 1], sleep_got)
        self.assertEqual([0], rst)


class TestJobManager(unittest.TestCase):

    def test_manager(self):

        rst = []

        def _sleep(args):
            time.sleep(0.1)
            return args

        def _collect(args):
            rst.append(args)

        jm = jobq.JobManager([_sleep, _collect])

        t0 = time.time()
        for i in range(3):
            jm.put(i)

        jm.join()

        t1 = time.time()

        self.assertEqual([0, 1, 2], rst)
        self.assertTrue(-0.05 < t1 - t0 - 0.3 < 0.05)

    def test_join_timeout(self):

        def _sleep(args):
            time.sleep(0.1)

        jm = jobq.JobManager([_sleep])

        t0 = time.time()
        for i in range(3):
            jm.put(i)

        jm.join(timeout=0.1)

        t1 = time.time()

        self.assertTrue(0.09 < t1 - t0 < 0.11)

    def test_stat(self):

        def _pass(args):
            return args

        jm = jobq.JobManager([_pass])

        for i in range(3):

            jm.put(i)

            time.sleep(0.01)
            st = jm.stat()

            # each element get in twice: _pass and _blackhole
            self.assertEqual((i + 1) * 2, st['in'])
            self.assertEqual((i + 1) * 2, st['out'])
            self.assertEqual(0, st['doing'])

        jm.join()

    def test_stat_on_builtin_method(self):

        rst = []
        jm = jobq.JobManager([rst.append])

        # stat() read attribute `func.__module__`.
        # But for builtin method, there is no __module__ attribute.

        # this should not raise
        jm.stat()

        jm.join()

    def test_set_thread_num(self):

        def _pass(args):
            return args

        rst = []

        jm = jobq.JobManager([_pass, rst.append])

        for invalid in (0, -1, 1.1):
            self.assertRaises(
                AssertionError, jm.set_thread_num, _pass, invalid)

        n = 10240
        for i in range(n):

            jm.put(i)

            # change thread number every 91 put
            if i % 91:
                # randomly change thread number
                jm.set_thread_num(_pass, i % 3 + 1)

        jm.join()

        rst.sort()
        for i in range(n):
            self.assertEqual(i, rst[i])

    def test_set_thread_num_with_object_method(self):
        """
        In python2, `x = X(); x.meth is x.meth` results in a `False`.
        Every time to retrieve a method, python creates a new **bound** function.

        See https://stackoverflow.com/questions/15977808/why-dont-methods-have-reference-equality
        """

        class X(object):

            def meth(self):
                pass

        x = X()

        jm = jobq.JobManager([x.meth])

        before = jm.stat()
        self.assertEqual(1, before['workers'][0]['nr_worker'])

        # This should not raise JobWorkerNotFound.
        jm.set_thread_num(x.meth, 2)

        after = jm.stat()
        self.assertEqual(2, after['workers'][0]['nr_worker'])

        jm.join()

    def test_set_thread_num_keep_order(self):

        def _pass(args):
            return args

        rst = []

        jm = jobq.JobManager([_pass, rst.append], keep_order=True)

        setter = {'running': True}

        def _change_thread_nr():
            while setter['running']:
                jm.set_thread_num(_pass, random.randint(1, 4))
                time.sleep(0.5)

        ths = []
        for ii in range(3):
            th = threadutil.start_daemon_thread(_change_thread_nr)
            ths.append(th)

        n = 10240
        for i in range(n):
            jm.put(i)

        jm.join()

        rst.sort()
        for i in range(n):
            self.assertEqual(i, rst[i])

        setter['running'] = False

        for th in ths:
            th.join()


class TestJobQ(unittest.TestCase):

    def test_exception(self):

        # Add a handler, or python complains "no handler assigned
        # to...."
        jl = logging.getLogger('pykit.jobq')
        jl.addHandler(logging.NullHandler())

        def err_on_even(args):
            if args % 2 == 0:
                raise Exception('even number')
            else:
                return args

        def collect(args):
            rst.append(args)

        rst = []
        jobq.run(range(10), [err_on_even, collect])
        self.assertEqual(list(range(1, 10, 2)), rst)

        # remove NullHandler
        jl.handlers = []

    def test_sequential(self):

        cases = (
                ([0, 1, 2], [add1], [1, 2, 3]),
                ([0, 1, 2], [add1, multi2], [2, 4, 6]),
                (range(3), [add1, (multi2, 1)], [2, 4, 6]),
                (range(100), [add1, (multi2, 1), discard_even], []),
                (range(100), [add1, discard_even], list(range(1, 101, 2))),
                (range(1024 * 10), [add1, multi2],
                 list(range(2, 1024 * 10 * 2 + 2, 2))),
        )

        def collect(args):
            rst.append(args)

        for inp, workers, out in cases:
            rst = []
            jobq.run(inp, workers + [collect])
            self.assertEqual(out, rst)

    def test_concurrent(self):

        cases = (
                (list(range(100)), [add1, (multi2_sleep, 10)],
                 list(range(2, 202, 2))
                 ),
                (range(100), [add1, (multi2_sleep, 10)],
                 list(range(2, 202, 2))
                 ),
                (range(1024 * 10), [add1, (multi2, 4)],
                 list(range(2, 1024 * 10 * 2 + 2, 2))
                 ),
        )

        def collect(args):
            rst.append(args)

        for inp, workers, out in cases:
            rst = []
            jobq.run(inp, workers + [collect])
            self.assertEqual(set(out), set(rst))

            rst = []
            jobq.run(inp, workers + [collect], keep_order=True)
            self.assertEqual(out, rst)

    def test_generator(self):

        def gen(args):
            for i in range(3):
                yield i
                time.sleep(0.1)

        def collect(args):
            rst.append(args)

        rst = []
        jobq.run(range(3), [(gen, 2), collect], keep_order=True)
        self.assertEqual([0, 1, 2] * 3, rst,
                         "generator should extract all before next")

        rst = []
        jobq.run(range(3), [(gen, 2), collect], keep_order=False)
        self.assertEqual(set([0, 1, 2]), set(rst),
                         "generator should get all")

        self.assertEqual(9, len(rst), 'nr of elts')


class TestDefaultTimeout(unittest.TestCase):

    def test_default_timeout_is_not_too_large(self):

        # Issue: threading.Thread.join does not accept a very large timeout
        # value

        def _sleep_1(args):
            time.sleep(0.02)

        jobq.run(range(1), [_sleep_1])


class TestLimitJobSpeed(unittest.TestCase):

    def test_limit_job_speed(self):

        job_num = 300
        job_speed = 100

        def entry_iter():
            for ii in xrange(job_num):
                yield ii

        def empty(num):
            pass

        t0 = time.time()

        jobq.run(entry_iter(), [
                (jobq.limit_job_speed(job_speed, 1), 1),
                (empty, 10),
        ])

        self.assertEqual(int(job_num / job_speed), int(time.time() - t0))
