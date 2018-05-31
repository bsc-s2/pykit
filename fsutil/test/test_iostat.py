#!/usr/bin/env python2
# coding: utf-8

import os
import shelve
import time
import unittest

from pykit import config
from pykit import fsutil
from pykit import threadutil
from pykit import ututil

dd = ututil.dd

rst_keys = ['read', 'write', 'ioutil']


class TestIostat(unittest.TestCase):

    def test_iostat(self):

        force_remove(config.iostat_stat_path)

        with ututil.Timer() as t:
            rst = fsutil.iostat('/dev/sda1')
            dd(rst)

            self.assertIsNotNone(rst)
            self.assertEqual(set(rst_keys),
                             set(rst.keys()))

            for k in rst_keys:
                self.assertGreaterEqual(rst[k], 0)

            self.assertGreaterEqual(t.spent(), 1.0)

        # read again

        with ututil.Timer() as t:
            rst = fsutil.iostat('/dev/sda1')
            dd(rst)

            self.assertIsNotNone(rst)
            self.assertEqual(set(rst_keys),
                             set(rst.keys()))

            for k in rst_keys:
                self.assertGreaterEqual(rst[k], 0)

            self.assertAlmostEqual(0.0, t.spent(), delta=0.1)

    def test_duration_is_negative(self):

        force_remove(config.iostat_stat_path)

        with ututil.Timer() as t:
            rst = fsutil.iostat('/dev/sda1')
            dd(rst)

            self.assertIsNotNone(rst)
            self.assertEqual(set(rst_keys),
                             set(rst.keys()))
            self.assertGreaterEqual(t.spent(), 1.0)

        d = shelve.open(config.iostat_stat_path)
        x = d['sda1']
        x['ts'] += 2
        d['sda1'] = x
        d.close()

        with ututil.Timer() as t:
            rst = fsutil.iostat('/dev/sda1')
            dd(rst)

            self.assertIsNotNone(rst)
            self.assertEqual(set(rst_keys),
                             set(rst.keys()))
            self.assertGreater(rst['write'], 0)
            self.assertGreaterEqual(t.spent(), 1.0)

    def test_path(self):

        rst = fsutil.iostat(path='/')
        dd(rst)

        self.assertIsNotNone(rst)
        self.assertEqual(set(rst_keys),
                         set(rst.keys()))

        for k in rst_keys:
            self.assertGreaterEqual(rst[k], 0)

    def test_ioutil_heavy_load(self):

        sess = {'running': True}

        def _write(i):
            while sess['running']:
                with open('/tmp/pykit-test-write-' + str(i), 'w') as f:
                    f.write('a' * 1024*1024*10)

        th1 = threadutil.start_daemon(_write, args=(1, ))
        th2 = threadutil.start_daemon(_write, args=(2, ))

        time.sleep(2)
        force_remove('/tmp/pykit-iostat')

        with ututil.Timer() as t:
            rst = fsutil.iostat('/dev/sda1')
            dd(rst)

            self.assertAlmostEqual(100, rst['ioutil'], delta=30)
            self.assertGreaterEqual(t.spent(), 1.0)

        sess['running'] = False
        th1.join()
        th2.join()

        force_remove('/tmp/pykit-test-write-1')
        force_remove('/tmp/pykit-test-write-2')

    def test_config(self):

        force_remove('/tmp/foo')

        # write to default place and then ensure config changes stat path

        rst = fsutil.iostat('/dev/sda1')

        # change stat path

        old = config.iostat_stat_path
        config.iostat_stat_path = '/tmp/foo'

        with ututil.Timer() as t:
            rst = fsutil.iostat('/dev/sda1')
            dd(rst)

            self.assertGreaterEqual(t.spent(), 1.0)

        # should be able to read something.
        fsutil.read_file(config.iostat_stat_path)

        force_remove(config.iostat_stat_path)
        config.iostat_stat_path = old


def force_remove(fn):

    try:
        os.rmdir(fn)
    except:
        pass

    try:
        os.unlink(fn)
    except:
        pass
