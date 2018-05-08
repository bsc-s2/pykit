#!/usr/bin/env python2
# coding: utf-8

import time
import unittest

from pykit import threadutil
from pykit import ututil

tu = threadutil.threadutil


def _work(sess):
    try:
        while True:
            x = 1

    except SystemExit:
        sess['raised'] = True


class TestThreadutil(unittest.TestCase):

    def _verify_exception_raised(self, sess, thread):
        # we wait few seconds for the exception to be raised.
        for i in range(100):
            if sess['raised']:
                # The thread might still be alive at this point.
                time.sleep(0.2)
                self.assertFalse(thread.is_alive())
                break

            time.sleep(0.1)

        else:
            assert False, "SystemError is not raised"

    def test_raise_in_thread(self):
        sess = {'raised': False}

        t = tu.start_thread(_work, args=(sess, ), daemon=True)
        self.assertFalse(sess['raised'])

        with self.assertRaises(TypeError):
            tu.raise_in_thread('thread', SystemExit)

        with self.assertRaises(TypeError):
            tu.raise_in_thread(t, SystemExit())

        class SomeClass(object):
            pass

        with self.assertRaises(ValueError):
            tu.raise_in_thread(t, SomeClass)

        tu.raise_in_thread(t, SystemExit)
        self._verify_exception_raised(sess, t)

    def test_raise_in_thread_many_times(self):
        sess = {'raised': False}

        t = tu.start_thread(_work, args=(sess, ), daemon=True)
        self.assertFalse(sess['raised'])

        for i in range(5):
            try:
                tu.raise_in_thread(t, SystemExit)
            except tu.InvalidThreadIdError:
                # This will happen if the thread is already terminated by
                # a previous raise_in_thread call.
                pass

        self._verify_exception_raised(sess, t)

        # Raising in a dead thread shoud not break.
        with self.assertRaises(tu.InvalidThreadIdError):
            tu.raise_in_thread(t, SystemExit)

    def test_start_thread(self):
        def _sort(a, reverse=False):
            a.sort(reverse=reverse)

        array = [3, 1, 2]
        t = tu.start_thread(_sort, args=(array, ))
        t.join()

        self.assertEqual(array, [1, 2, 3])

        t = tu.start_thread(_sort, args=(array, ),
                            kwargs={'reverse': True})
        t.join()

        self.assertEqual(array, [3, 2, 1])

    def test_start_daemon(self):
        def noop(): return None

        # Thread should be non-daemon by default
        t = tu.start_thread(noop)
        self.assertFalse(t.daemon)

        t = tu.start_thread(noop, daemon=True)
        self.assertTrue(t.daemon)

        t = tu.start_daemon(noop)
        self.assertTrue(t.daemon)

    def test_thread_after(self):

        def _do():
            pass

        with ututil.Timer() as t:
            th = tu.start_thread(target=_do, after=None)
            th.join()
            self.assertAlmostEqual(0, t.spent(), delta=0.1)

        with ututil.Timer() as t:
            th = tu.start_thread(target=_do, after=0.5)
            th.join()
            self.assertAlmostEqual(0.5, t.spent(), delta=0.1)

    def test_daemon_after(self):

        def _do():
            pass

        with ututil.Timer() as t:
            th = tu.start_daemon(target=_do, after=None)
            th.join()
            self.assertAlmostEqual(0, t.spent(), delta=0.1)

        with ututil.Timer() as t:
            th = tu.start_daemon(target=_do, after=0.5)
            th.join()
            self.assertAlmostEqual(0.5, t.spent(), delta=0.1)
