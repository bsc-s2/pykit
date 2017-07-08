#!/usr/bin/env python2
# coding: utf-8

import os
import time
import unittest

from pykit import processutil

this_base = os.path.dirname(os.path.realpath(__file__))


class TestProcessutil(unittest.TestCase):

    foo_fn = '/tmp/foo'

    def _read_file(self, fn):
        try:
            with open(fn, 'r') as f:
                cont = f.read()
                return cont
        except EnvironmentError:
            return None

    def test_start_exec_process(self):

        cases = (
            ('python2', this_base + '/a.py', ['foo'], 'foo'),
            ('python2', this_base + '/a.py', ['foo', 'bar'], 'foobar'),
            ('sh', this_base + '/a.sh', ['123'], '123'),
            ('sh', this_base + '/a.sh', ['123', '456'], '123456'),
        )

        for cmd, target, args, expected in cases:
            processutil.start_exec_process(cmd, target, *args)
            time.sleep(1)
            self.assertEqual(expected, self._read_file(self.foo_fn))
