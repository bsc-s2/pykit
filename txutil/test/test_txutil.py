import threading
import unittest

from pykit import threadutil
from pykit import txutil
from pykit import ututil

dd = ututil.dd


class TestCASLoop(unittest.TestCase):

    def setUp(self):
        self.lock = threading.RLock()
        self.val = 0
        self.ver = 0

    def tearDown(self):
        pass

    def _get(self, key):
        with self.lock:
            return self.val, self.ver

    def _set(self, key, val, prev_stat):
        with self.lock:
            if prev_stat != self.ver:
                return False
            else:
                self.val = val
                self.ver += 1
                return True

    def test_cas(self):

        for curr in txutil.cas_loop(self._get, self._set, 'foo'):
            self.assertEqual(0, curr.stat)
            curr.v += 2

        self.assertEqual((2, 1), (self.val, self.ver))

    def test_cas_abort(self):

        for curr in txutil.cas_loop(self._get, self._set, 'foo'):
            curr.v += 2
            break

        self.assertEqual((0, 0), (self.val, self.ver))

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
