#!/usr/bin/env python2
# coding: utf-8

import os
import time
import unittest

from pykit import daemonize
from pykit import proc
from pykit import ututil

dd = ututil.dd

this_base = os.path.dirname(__file__)


def subproc(script, env=None):
    if env is None:
        env = dict(PYTHONPATH=this_base + '/../..',)

    return proc.shell_script(script, env=env)


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
            dd(repr(e))

        time.sleep(0.1)

        try:
            subproc('python2 {b}/bar.py stop'.format(b=this_base))
        except Exception as e:
            dd(repr(e))

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

    def test_default_pid_file(self):

        d = daemonize.Daemon()
        self.assertEqual('/var/run/__main__', d.pidfile)

    def test_close_fds(self):
        env = dict(PYTHONPATH='{path_daemonize}:{path_pykit}'.format(
                              path_daemonize=this_base + '/../..',
                              path_pykit=this_base + '/../../..'))

        subproc('python2 {b}/close_fds.py close'.format(b=this_base), env=env)
        time.sleep(0.2)

        fds = read_file(self.foo_fn)

        self.assertNotIn(self.bar_fn, fds)

        subproc('python2 {b}/close_fds.py open'.format(b=this_base), env=env)
        time.sleep(0.2)

        fds = read_file(self.foo_fn)

        self.assertIn(self.bar_fn, fds)
