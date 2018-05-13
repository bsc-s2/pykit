import threading
import unittest

from pykit import threadutil
from pykit import txutil
from pykit import ututil

dd = ututil.dd


class MyError(Exception):
    pass


class TestCASLoop(unittest.TestCase):

    def setUp(self):
        self.lock = threading.RLock()
        self.val = 0
        self.ver = 0

    def tearDown(self):
        pass

    def _get(self):
        with self.lock:
            return self.val, self.ver

    def _set(self, val, prev_stat):
        with self.lock:
            if prev_stat != self.ver:
                raise txutil.CASConflict(prev_stat, self.ver)
            self.val = val
            self.ver += 1

    def _set_raise_myerror(self, val, prev_stat):
        with self.lock:
            raise MyError(prev_stat, self.ver)

    def test_cas(self):

        i = 0
        for curr in txutil.cas_loop(self._get, self._set):
            self.assertEqual(i, curr.stat)
            curr.v += 2

    def test_cas_n(self):

        i = 0
        for curr in txutil.cas_loop(self._get, self._set_raise_myerror,
                                    conflicterror=MyError):
            self.assertEqual(i, curr.n)
            i += 1
            if i == 5:
                break

    def test_cas_abort(self):

        for curr in txutil.cas_loop(self._get, self._set):
            curr.v += 2
            break

        self.assertEqual((0, 0), (self.val, self.ver))

    def test_cas_customed_error(self):

        for curr in txutil.cas_loop(self._get, self._set_raise_myerror,
                                    conflicterror=MyError):
            curr.v += 2
            if curr.n == 5:
                break

        self.assertEqual((0, 0), (self.val, self.ver))

    def test_cas_argument(self):

        rst = {}

        def _get(*args, **kwargs):
            rst['get'] = args, kwargs
            return 'val', 'stat'

        def _set(*args, **kwargs):
            rst['set'] = args, kwargs

        for curr in txutil.cas_loop(_get, _set, ('foo', 'bar'), dict(a=1, b=2)):
            curr.v = 'uservalue'

        self.assertEqual((('foo', 'bar'), {"a": 1, "b": 2}), rst['get'])
        self.assertEqual((('foo', 'bar', 'uservalue', 'stat'), {"a": 1, "b": 2}), rst['set'])

        # empty arg

        rst = {}

        for curr in txutil.cas_loop(_get, _set):
            curr.v = 'uservalue'

        self.assertEqual(((), {}), rst['get'])
        self.assertEqual((('uservalue', 'stat'), {}), rst['set'])

    def test_cas_concurrent(self):

        def _update():
            for ii in range(10):
                for curr in txutil.cas_loop(self._get, self._set):
                    curr.v += 1

        ths = [threadutil.start_daemon(_update)
               for _ in range(10)]

        for th in ths:
            th.join()

        self.assertEqual((100, 100), (self.val, self.ver))
