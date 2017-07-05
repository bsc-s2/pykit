#!/usr/bin/env python2
# conding: utf-8

import os
import sys
import unittest

from pykit import shell

class TestS2Command(unittest.TestCase):

    def setUp(self):
        self.out_buf = os.getcwd() + 'out_buf'
        self.backup_sys = sys.argv
        sys.argv = sys.argv[:1]

    def tearDown(self):
        sys.argv = self.backup_sys
        os.remove(self.out_buf)

    def test_command_normal_output(self):

        arguments = {'hello': lambda *x: sys.stdout.write(repr(x))}

        sys.argv.append('hello')
        sys.argv.append('hello_world')

        backup = sys.stdout
        with open(self.out_buf, 'w') as fw:
            sys.stdout = fw
            try:
                shell.command_normal(**arguments)
            except (SystemExit) as e:
                if len(e.args) > 0:
                    self.assertEqual(0, e.args[0])

        sys.stdout = backup
        with open(self.out_buf, 'r') as fr:
            s = fr.readline()
            self.assertEqual(s, "('hello_world',)")

        sys.argv = sys.argv[:1]

        sys.argv.append('err_hello')
        backup = sys.stderr
        with open(self.out_buf, 'w') as fw:
            sys.stderr = fw
            try:
                shell.command_normal(**arguments)
            except (SystemExit) as e:
                if len(e.args) > 0:
                    self.assertEqual(2, e.args[0])

        sys.stderr = backup
        with open(self.out_buf, 'r') as fr:
            s = fr.readline()
            self.assertEqual(s, "No such command: err_hello")

        sys.argv = sys.argv[:1]

    def test_command_normal_error(self):

        arguments = {'err': lambda x, y:  int(x) / int(y)}

        sys.argv.extend(['err', '7', '0']);
        backup = sys.stderr
        with open(self.out_buf, 'w') as fw:
            sys.stderr = fw
            try:
                shell.command_normal(**arguments)
            except SystemExit as e:
                if len(e.args) > 0:
                    self.assertEqual(1, e.args[0])
            except ZeroDivisionError as e:
                pass

        sys.stderr = backup
        with open(self.out_buf, 'r') as fr:
            s = fr.readline()
            self.assertEqual(s, "ZeroDivisionError('integer division or modulo by zero',)")

        sys.argv = sys.argv[:1]

        sys.argv.extend(['err', '7', '3'])
        try:
            shell.command_normal(**arguments)
        except SystemExit as e:
            if len(e.args) > 0:
                self.assertEqual(1, e.args[0])

        sys.argv = sys.argv[:1]

    def test_command_normal_wrong_command(self):

        arguments = {
                'foo': {
                    'bob': {
                        'alice': lambda *x: sys.stdout.write(repr('alice'))
                    }
                }
            }

        sys.argv.extend(['foo', 'bob', 'alice'])
        backup = sys.stdout
        with open(self.out_buf, 'w') as fw:
            sys.stdout = fw
            try:
                shell.command_normal(**arguments)
            except SystemExit as e:
                if len(e.args) > 0:
                    self.assertEqual(0, e.args[0])

        sys.stdout = backup
        with open(self.out_buf, 'r') as fr:
            s = fr.readline()
            self.assertEqual(s, "'alice'")

        sys.argv = sys.argv[:1]

        sys.argv.extend(['foo', 'bob'])
        backup = sys.stderr
        with open(self.out_buf, 'w') as fw:
            sys.stderr = fw
            try:
                shell.command_normal(**arguments)
            except SystemExit as e:
                if len(e.args) > 0:
                    self.assertEqual(2, e.args[0])

        sys.stderr = backup
        with open(self.out_buf, 'r') as fr:
            s = fr.readline()
            self.assertEqual(s, 'No such command: foo bob')

        sys.argv = sys.argv[:1]

