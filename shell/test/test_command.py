#!/usr/bin/env python2
# conding: utf-8

import os
import sys
import unittest
import logging

from pykit import shell

class TestCommand(unittest.TestCase):

    def setUp(self):
        self.out_buf = os.path.join(os.getcwd(), 'out_buf')
        self.backup_argv = sys.argv
        sys.argv = sys.argv[:1]

        logging.basicConfig(level=logging.CRITICAL)

    def tearDown(self):
        sys.argv = self.backup_argv
        try:
            os.remove(self.out_buf)
        except EnvironmentError as e:
            sys.stderr.write(repr(e))

    def excute_test(self, arguments, argv, out_str, exit_code):

        sys.argv.extend(argv)

        backup_stderr = sys.stderr

        with open(self.out_buf, 'w') as fw:
            sys.stderr = fw

            try:
                shell.command(**arguments)
            except SystemExit as e:
                if len(e.args) > 0:
                    self.assertEqual(exit_code, e.args[0])

        sys.stderr = backup_stderr

        with open(self.out_buf, 'r') as fr:
            s = fr.read()
            self.assertEqual(s, out_str)

        sys.argv = sys.argv[:1]

    def test_command_no_such_command(self):

        testcases = (
            (
                {'echo': lambda *x: sys.stderr.write(repr(x))},
                [],
                'No such command: ',
                2,
            ),
            (
                {'echo': lambda *x: sys.stderr.write(repr(x))},
                ['echoo'],
                'No such command: echoo',
                2,
            ),
            (
                {'call': 'not_callable'},
                ['call'],
                'No such command: call',
                2,
            )
        )

        for arguments, argv, out_str, exit_code in testcases:
            self.excute_test(arguments, argv, out_str, exit_code)

    def test_command_execute_error(self):

        testcases = (
            (
                {'divi': lambda x, y: int(x)/int(y)},
                ['divi'],
                "TypeError('<lambda>() takes exactly 2 arguments (0 given)',)",
                1,
            ),
            (
                {'mod': {
                    'mod_2': lambda x: int(x)%2,
                    },
                },
                ['mod', 'mod_2'],
                "TypeError('<lambda>() takes exactly 1 argument (0 given)',)",
                1,
            ),
            (
                {'divi': lambda x, y: int(x)/int(y)},
                ['divi', '7', '0'],
                "ZeroDivisionError('integer division or modulo by zero',)",
                1,
            ),
            (
                {'divi': lambda x, y: int(x)/int(y)},
                ['divi', 'string', 'number'],
                '''ValueError("invalid literal for int() with base 10: \'string\'",)''',
                1,
            ),
        )

        for arguments, argv, out_str, exit_code in testcases:
            self.excute_test(arguments, argv, out_str, exit_code)

    def test_command_execute_normal(self):

        testcases = (
            (
                {'echo_repr': lambda *x: sys.stderr.write(repr(x))},
                ['echo_repr', 'hello_world'],
                "('hello_world',)",
                0,
            ),
            (
                {'divi': lambda x, y: int(x)/int(y)},
                ['divi', '7', '3'],
                '',
                1,
            ),
            (
                {'mod': {
                    'mod_2':lambda x: int(x)%2,
                    }
                },
                ['mod', 'mod_2', '3'],
                '',
                1,
            ),
        )

        for arguments, argv, out_str, exit_code in testcases:
            self.excute_test(arguments, argv, out_str, exit_code)

