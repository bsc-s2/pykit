#!/usr/bin/env python2
# coding: utf-8

import os
import subprocess
import time
import unittest

this_base = os.path.dirname(__file__)


def subproc(script):

    subproc = subprocess.Popen(['sh'],
                               close_fds=True,
                               env=dict(
                                       PYTHONPATH=this_base + '/../..',
                               ),
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    out, err = subproc.communicate(script)

    subproc.wait()

    if subproc.returncode != 0:
        print out
        print err

    return (subproc.returncode, out, err)


def read_file(fn):
    try:
        with open(fn, 'r') as f:
            cont = f.read()
            return cont
    except EnvironmentError:
        return None


class TestDaemonize(unittest.TestCase):

    foo_fn = '/tmp/foo'
    bar_fn = '/tmp/bar'
    pidfn = '/tmp/test_daemonize.pid'

    def _clean(self):

        # kill foo.py and kill bar.py
        # bar.py might be waiting for foo.py to release lock-file.
        try:
            subproc('python2 {b}/foo.py stop'.format(b=this_base))
        except Exception as e:
            print repr(e)

        time.sleep(0.1)

        try:
            subproc('python2 {b}/bar.py stop'.format(b=this_base))
        except Exception as e:
            print repr(e)

        # remove written file

        try:
            os.unlink(self.foo_fn)
        except EnvironmentError as e:
            pass

        try:
            os.unlink(self.bar_fn)
        except EnvironmentError as e:
            pass

    def setUp(self):
        self._clean()

    def tearDown(self):
        self._clean()

    def test_start(self):

        subproc('python2 {b}/foo.py start'.format(b=this_base))
        time.sleep(0.2)

        self.assertEqual('foo-before', read_file(self.foo_fn))
        time.sleep(1)
        self.assertEqual('foo-after', read_file(self.foo_fn))

    def test_stop(self):

        subproc('python2 {b}/foo.py start'.format(b=this_base))
        time.sleep(0.2)

        self.assertEqual('foo-before', read_file(self.foo_fn), 'foo started')

        subproc('python2 {b}/foo.py stop'.format(b=this_base))
        time.sleep(0.2)

        self.assertEqual('foo-before', read_file(self.foo_fn),
                         'process has been kill thus no content is updated')

    def test_restart(self):

        subproc('python2 {b}/foo.py start'.format(b=this_base))
        time.sleep(0.2)

        self.assertEqual('foo-before', read_file(self.foo_fn))

        os.unlink(self.foo_fn)
        self.assertEqual(None, read_file(self.foo_fn))

        subproc('python2 {b}/foo.py restart'.format(b=this_base))
        time.sleep(0.2)

        self.assertEqual('foo-before', read_file(self.foo_fn),
                         'restarted and rewritten to the file')

    def test_exclusive_pid(self):

        subproc('python2 {b}/foo.py start'.format(b=this_base))
        time.sleep(0.1)
        subproc('python2 {b}/bar.py start'.format(b=this_base))
        time.sleep(0.1)

        self.assertEqual(None, read_file(self.bar_fn),
                         'bar.py not started or run')
