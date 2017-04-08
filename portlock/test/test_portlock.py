import threading
import time
import unittest

from pykit import portlock
from pykit import ututil

dd = ututil.dd


class TestPortlock(unittest.TestCase):

    def test_mem_test(self):

        a = portlock.Portlock('k1')
        b = portlock.Portlock('k1')

        dd('lock-a: ', a.addr)
        dd('lock-b: ', b.addr)

        r = b.has_locked()
        self.assertFalse(r, 'not locked')

        r = b.has_locked()
        self.assertFalse(r, 'still not locked')

        a.acquire()

        r = b.has_locked()
        self.assertFalse(r, 'not locked by me.')

        r = b.try_lock()
        self.assertFalse(r, 'can not lock while another one hold it')

        b.release()
        r = b.try_lock()
        self.assertFalse(r, 'b can not release lock belongs to a')

        a.release()

        r = b.try_lock()
        self.assertTrue(r, 'I can hold it now')
        dd('try-locked:', r)

        try:
            a.acquire()
            self.fail("lock-a should not be able to get lock")
        except portlock.PortlockError:
            pass

    def test_1_lock_per_thread(self):

        sess = {'n': 0}

        def worker(l, ident):
            for ii in range(1000):
                l.acquire()
                dd('{0}-{1} start'.format(ident, ii))

                self.assertEqual(
                    0, sess['n'], 'n is 0 just after lock is acquired, 1-lock-for-1')

                sess['n'] += 1
                time.sleep(0.001)
                self.assertEqual(
                    1, sess['n'], "no more than 2 thread holding lock")
                sess['n'] -= 1
                dd('{0}-{1} end'.format(ident, ii))
                l.release()

        ts = [threading.Thread(
            target=worker,
            args=(portlock.Portlock('x', timeout=100),
                  x))
              for x in range(10)]

        for t in ts:
            t.start()

        for t in ts:
            t.join()

    def test_1_lock_for_all_thread(self):

        sess = {'n': 0}

        def worker(l):
            for ii in range(1000):
                l.acquire()

                self.assertEqual(
                    0, sess['n'], 'n is 0 just after lock is acquired, 1-lock-for-all')

                sess['n'] += 1
                time.sleep(0.001)
                self.assertEqual(
                    1,  sess['n'], "no more than 2 thread holding lock")
                sess['n'] -= 1
                l.release()

        lock = portlock.Portlock('x', timeout=100)
        ts = [threading.Thread(target=worker,
                               args=(lock, ))
              for x in range(3)]

        for t in ts:
            t.daemon = True
            t.start()

        for t in ts:
            t.join()

    def test_sleep_time(self):

        lock0 = portlock.Portlock('x')
        lock = portlock.Portlock('x', timeout=1, sleep_time=2)

        with lock0:

            t0 = time.time()
            try:
                lock.acquire()
            except portlock.PortlockTimeout:
                pass

            t1 = time.time()

            self.assertTrue(0.9 < t1 - t0 < 1.1,
                            'sleep_time should not affect timeout(1 sec),'
                            ' but it spends {0} seconds'.format(t1 - t0))
