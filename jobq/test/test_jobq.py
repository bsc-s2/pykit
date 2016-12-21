import time
import unittest

import jobq


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

    def test_probe(self):
        probe = {}
        jobq.run(range(10), [multi2], probe=probe)
        stat = jobq.stat(probe)
        self.assertEqual(2, len(stat))
        self.assertEqual(True, stat[0]['name'].endswith('multi2'))
        self.assertEqual(0, stat[0]['input']['size'])
        self.assertEqual(True, stat[0]['input']['capa'] > 0)


class TestJobQ(unittest.TestCase):

    def test_timeout(self):

        def collect(args):
            rst.append(args)

        rst = []
        jobq.run(range(10), [sleep_5, collect], timeout=0.1)
        self.assertEqual([], rst)

    def test_exception(self):

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
            time.sleep(1)

        jobq.run(range(1), [_sleep_1])

if __name__ == "__main__":
    unittest.main()
