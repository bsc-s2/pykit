#!/usr/bin/env python2
# coding: utf-8

import unittest
import threading
import time

from pykit.threadutil import threadutil


def _work(sess):
    try:
        while True:
            time.sleep(0.1)
    except SystemExit:
        sess['raised'] = True


class TestThreadutil(unittest.TestCase):

    def _verify_exception_raised(self, sess, thread):
        # we wait few seconds for the exception to be raised.
        for i in range(50):
            if sess['raised']:
                self.assertFalse(thread.is_alive())
                break

            time.sleep(0.1)

        else:
            assert False, "SystemError is not raised"

    def test_raise_in_thread(self):
        sess = {'raised': False}

        t = threading.Thread(target=_work, args=(sess, ))
        t.daemon = True
        t.start()

        self.assertFalse(sess['raised'])

        with self.assertRaises(TypeError):
            threadutil.raise_in_thread('thread', SystemExit)

        with self.assertRaises(TypeError):
            threadutil.raise_in_thread(t, SystemExit())

        class SomeClass(object):
            pass

        with self.assertRaises(ValueError):
            threadutil.raise_in_thread(t, SomeClass)

        threadutil.raise_in_thread(t, SystemExit)
        self._verify_exception_raised(sess, t)

    def test_raise_in_thread_many_times(self):
        sess = {'raised': False}

        t = threading.Thread(target=_work, args=(sess, ))
        t.daemon = True
        t.start()

        self.assertFalse(sess['raised'])

        for i in range(10):
            threadutil.raise_in_thread(t, SystemExit)

        self._verify_exception_raised(sess, t)

        # Raising in a dead thread shoud not break.
        threadutil.raise_in_thread(t, SystemExit)
