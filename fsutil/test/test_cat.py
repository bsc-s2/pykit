#!/usr/bin/env python2
# coding: utf-8

import os
import time
import unittest

from pykit import fsutil
from pykit import proc
from pykit import threadutil
from pykit import ututil

dd = ututil.dd

# xx/pykit/fsutil/test/
this_base = os.path.dirname(__file__)

pyt = 'python2'


class TestCat(unittest.TestCase):

    fn = '/tmp/pykit-cat-test-content'

    def setUp(self):
        force_remove(self.fn)

    def tearDown(self):
        force_remove(self.fn)

    def test_entire_file(self):

        expected = [
            'a',
            'bcd',
        ]

        append_lines(self.fn, expected)

        rst = []
        for l in fsutil.Cat(self.fn, strip=True).iterate(timeout=0):
            rst.append(l)

        self.assertEqual(expected, rst)

    def test_entire_large_file(self):

        expected = [
            'a' * 1024 * 32,
            'b' * 1024 * 32,
        ] * 1024

        append_lines(self.fn, expected)

        dd(os.system('ls -l /tmp/pykit*'))

        rst = []
        for l in fsutil.Cat(self.fn, strip=True).iterate(timeout=0):
            rst.append(l)

        self.assertEqual(expected, rst)

    def test_offset_record_when_destory(self):

        expected = [ x * 32 for x in 'qwertyuiop' ]
        rst = []

        append_lines(self.fn, expected)
        for _ in expected:
            val = fsutil.Cat(self.fn, strip=True).iterate(timeout=0).next()
            rst.append(val)

        self.assertEqual(expected, rst)

    def test_continue_read(self):

        expected = [
            'a' * 32,
            'b' * 32,
        ]
        rst = []

        append_lines(self.fn, expected)

        for l in fsutil.Cat(self.fn, strip=True).iterate(timeout=0):
            rst.append(l)

        append_lines(self.fn, expected)

        for l in fsutil.Cat(self.fn, strip=True).iterate(timeout=0):
            rst.append(l)

        self.assertEqual(expected * 2, rst)

    def test_wait_for_file(self):

        expected = [
            'a' * 32,
            'b' * 32,
        ]
        rst = []

        def _append():
            time.sleep(0.1)
            append_lines(self.fn, expected)
            dd('appended')

        th = threadutil.start_daemon_thread(_append)

        try:
            for l in fsutil.Cat(self.fn, strip=True).iterate(timeout=0.4):
                rst.append(l)
        except fsutil.NoData:
            pass

        th.join()

        self.assertEqual(expected, rst)

    def test_wait_for_file_timeout(self):

        expected = [
            'a' * 32,
            'b' * 32,
        ]
        rst = []

        def _append():
            time.sleep(0.3)
            append_lines(self.fn, expected)
            dd('appended')

        th = threadutil.start_daemon_thread(_append)

        try:
            for l in fsutil.Cat(self.fn, strip=True).iterate(timeout=0.1):
                rst.append(l)

            self.failed('expect NoSuchFile to raise')
        except fsutil.NoSuchFile:
            pass

        self.assertEqual([], rst)

        th.join()

    def test_wait_for_data(self):

        expected = [
            'a' * 32,
            'b' * 32,
        ]
        rst = []

        append_lines(self.fn, expected)

        def _append():
            for _ in range(5):
                time.sleep(0.1)
                append_lines(self.fn, expected)
            dd('appended')

        th = threadutil.start_daemon_thread(_append)

        try:
            for l in fsutil.Cat(self.fn, strip=True).iterate(timeout=0.3):
                rst.append(l)

            self.failed('expect NoData to raise')
        except fsutil.NoData:
            pass

        th.join()
        self.assertEqual(expected * 6, rst)

    def test_wait_for_data_timeout(self):

        expected = [
            'a' * 32,
            'b' * 32,
        ]
        rst = []

        append_lines(self.fn, expected)
        dd('appended 1')

        def _append():
            time.sleep(0.3)
            append_lines(self.fn, expected)
            dd('appended')

        th = threadutil.start_daemon_thread(_append)

        try:
            for l in fsutil.Cat(self.fn, strip=True).iterate(timeout=0.1):
                rst.append(l)

            self.failed('expect NoData to raise')
        except fsutil.NoData:
            pass

        th.join()
        self.assertEqual(expected, rst)

    def test_exclusive(self):

        append_lines(self.fn, ['x'])

        # by default it is exclusive
        a = fsutil.Cat(self.fn, strip=True).iterate(timeout=0.1)
        b = fsutil.Cat(self.fn, strip=True).iterate(timeout=0.1)

        val = a.next()
        self.assertEqual('x', val)
        self.assertRaises(fsutil.LockTimeout, b.next)

        # non-exclusive still work
        # a has not yet quit, thus it has not yet written offset to stat file.
        c = fsutil.Cat(self.fn, strip=True, exclusive=False).iterate(timeout=0.1)
        val = c.next()
        self.assertEqual('x', val)

    def test_handler(self):

        expected = [
            'a' * 32,
            'b' * 32,
        ]
        append_lines(self.fn, expected)

        rst = []
        c = fsutil.Cat(self.fn, strip=True, handler=rst.append)
        c.cat(timeout=0)
        self.assertEqual(expected, rst)

        # handler is a list of callable
        exp = []
        for l in expected:
            exp.append(l)
            exp.append(l)

        rst = []
        force_remove(self.fn)
        append_lines(self.fn, expected)
        c = fsutil.Cat(self.fn, strip=True, handler=[rst.append, rst.append])
        c.cat(timeout=0)

        self.assertEqual(exp, rst)

    def test_file_end_handler(self):
        expected = [
            'a' * 32,
            'b' * 32,
        ]
        append_lines(self.fn, expected)

        rst = []

        def _end():
            rst.append('end')

        # file_end_handler in cat()
        c = fsutil.Cat(self.fn, strip=True, handler=rst.append, file_end_handler=_end)
        c.cat(timeout=0)
        self.assertEqual(expected + ['end'], rst)

        # file_end_handler in iterate()
        rst = []
        force_remove(self.fn)
        append_lines(self.fn, expected)
        for line in fsutil.Cat(self.fn, strip=True, file_end_handler=_end).iterate(timeout=0):
            rst.append(line)
        self.assertEqual(expected + ['end'], rst)

        # file_end_handler multi times
        rst = []
        force_remove(self.fn)
        append_lines(self.fn, expected)

        def _append():
            time.sleep(0.1)
            append_lines(self.fn, expected)

        th = threadutil.start_daemon_thread(_append)

        try:
            for line in fsutil.Cat(self.fn, strip=True, file_end_handler=_end).iterate(timeout=0.2):
                rst.append(line)
        except fsutil.NoData:
            pass

        th.join()
        self.assertEqual((expected + ['end']) * 2, rst)

    def test_cat(self):
        self.test_handler()

    def test_strip(self):

        expected = [
            'a' * 32,
            'b' * 32,
        ]
        append_lines(self.fn, expected)

        # by default do not strip
        rst = []
        for line in fsutil.Cat(self.fn).iterate(timeout=0):
            rst.append(line)

        self.assertEqual([x + '\n' for x in expected], rst)

    def test_id(self):
        expected = [
            'a' * 32,
            'b' * 32,
        ]
        append_lines(self.fn, expected)

        # different id does not block each other even they cat a same file
        a = fsutil.Cat(self.fn, id='foo', strip=True).iterate(timeout=0)
        b = fsutil.Cat(self.fn, id='bar', strip=True).iterate(timeout=0)

        self.assertEqual(expected[0], a.next())
        self.assertEqual(expected[0], b.next())

    def test_config(self):
        expected = [
            'a' * 32,
            'b' * 32,
        ]
        append_lines(self.fn, expected)

        rc, out, err = proc.shell_script(
            pyt + ' ' + this_base + '/cat/cat_load_config.py ' + self.fn,
            env=dict(PYTHONPATH=this_base + ':' + os.environ.get('PYTHONPATH'))
        )

        dd(rc)
        dd(out)
        dd(err)

        self.assertEqual(0, rc)

        path = [
            'fsutil_cat_lock_',
            'cat_load_config.py',
        ] + os.path.realpath(self.fn)[1:].split(os.path.sep)
        path = './' + '!'.join(path)
        dd(path)

        self.assertTrue(os.path.isfile(path))

        force_remove(path)


def force_remove(fn):

    try:
        os.rmdir(fn)
    except:
        pass

    try:
        os.unlink(fn)
    except:
        pass


def append_lines(fn, lines):

    with open(fn, 'a') as f:
        for l in lines:
            f.write(l + '\n')
        f.flush()
        os.fsync(f.fileno())
