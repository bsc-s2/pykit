#!/usr/bin/env python2
# coding: utf-8

import unittest

import humannum


class TestHumannum(unittest.TestCase):

    def test_humanize_number(self):

        cases = (
                (0,                        '0',    ''),
                (1,                        '1',    ''),
                (1.0,                   '1.00',    ''),
                (1.01,                  '1.01',    ''),
                (1.001,                 '1.00',    ''),
                (1023,                  '1023',    ''),
                (1024,                    '1K',    ''),
                (1024 + 1,             '1.00K',    ''),
                (1024 + 10,            '1.01K',    ''),
                (1024132,            '1000.1K',    ''),

                (1024 ** 2,               '1M',    ''),
                (1024 ** 2 + 10240,    '1.01M',    ''),
                (1024 ** 3,               '1G',    ''),
                (1024 ** 4,               '1T',    ''),
                (1024 ** 5,               '1P',    ''),
                (1024 ** 6,               '1E',    ''),
                (1024 ** 7,               '1Z',    ''),
                (1024 ** 8,               '1Y',    ''),
                (1024 ** 9,            '1024Y',    ''),
                (1024 ** 10,        '1048576Y',    ''),

                (1048996,              '1.00M',    ''),

                (True,                    True,    ''),
        )

        for _in, _out, _mes in cases:

            rst = humannum.humannum(_in)

            mes = 'humanize: in: {_in} expect: {_out}, rst: {rst}; {_mes}'.format(
                _in=repr(_in),
                _out=repr(_out),
                rst=rst,
                _mes=_mes
            )

            self.assertEqual(_out, rst, mes)

    def test_parse_number(self):

        cases = (
                ('0',         0,             ''),
                ('1',         1,             ''),
                ('1.00',      1.0,           ''),
                ('1.01',      1.01,          ''),
                ('1.00',      1,             ''),
                ('1023',      1023,          ''),
                ('1K',        1024,          ''),
                ('1.00K',     1024,          ''),
                ('1.01K',     1024 + 10.24,  ''),
                ('1000.1K',   1024102.4,     ''),
                ('1M',        1024 ** 2,     ''),
                ('1.01M',     1059061.76,    ''),
                ('1G',        1024 ** 3,     ''),
                ('1T',        1024 ** 4,     ''),
                ('1P',        1024 ** 5,     ''),
                ('1E',        1024 ** 6,     ''),
                ('1Z',        1024 ** 7,     ''),
                ('1Y',        1024 ** 8,     ''),
                ('1024Y',     1024 ** 9,     ''),
                ('1048576Y',  1024 ** 10,    ''),
                ('1.00M',     1048576,       ''),
        )

        for _in, _out, _mes in cases:

            rst = humannum.parsenum(_in)

            mes = 'parse: in: {_in} expect: {_out}, rst: {rst}; {_mes}'.format(
                _in=repr(_in),
                _out=repr(_out),
                rst=rst,
                _mes=_mes
            )

            self.assertEqual(_out, rst, mes)

            self.assertEqual(int(_out), humannum.parseint(_in),
                             mes + '; parseint')

            self.assertEqual(int(_out), humannum.parseint(_in + 'B'),
                             mes + '; parseint and suffix "B"')

            self.assertEqual(int(_out), humannum.parseint(_in + 'i'),
                             mes + '; parseint and suffix "i"')

    def test_specified_unit(self):

        cases = (
                ((1024 ** 2, {'unit': 1024}),      '1024K',   ''),
                ((1024 ** 2, {'unit': 1024**3}),   '0.001G',  ''),
        )

        for _in, _out, _mes in cases:

            rst = humannum.humannum(_in[0], **_in[1])

            mes = 'in: {_in} expect: {_out}, rst: {rst}; {_mes}'.format(
                _in=repr(_in),
                _out=repr(_out),
                rst=rst,
                _mes=_mes
            )

            self.assertEqual(_out, rst, mes)

    def test_non_primitive(self):

        cases = (
                ({'a': 10240},              {'a': '10K'},              ''),
                ([{'a': 10240}, 1024432],   [{'a': '10K'}, '1000.4K'], ''),
                ([{'a': 'xp'},  1024432],   [{'a': 'xp'}, '1000.4K'], ''),
        )

        for _in, _out, _mes in cases:

            rst = humannum.humannum(_in)

            mes = 'in: {_in} expect: {_out}, rst: {rst}; {_mes}'.format(
                _in=repr(_in),
                _out=repr(_out),
                rst=rst,
                _mes=_mes
            )

            self.assertEqual(_out, rst, mes)
            self.assertTrue(_in is not rst, 'result must not be input')

    def test_limit_keys(self):

        cases = (
                (({'a': 10240, 'b': 10240}, {'include': ['a', 'inexistent']}),
                 {'a': '10K', 'b': 10240},
                 ''
                 ),
                (({'a': 10240, 'b': 10240}, {'exclude': ['b', 'inexistent']}),
                 {'a': '10K', 'b': 10240},
                 ''
                 ),
        )

        for _in, _out, _mes in cases:

            rst = humannum.humannum(_in[0], **_in[1])

            mes = 'in: {_in} expect: {_out}, rst: {rst}; {_mes}'.format(
                _in=repr(_in),
                _out=repr(_out),
                rst=rst,
                _mes=_mes
            )

            self.assertEqual(_out, rst, mes)
            self.assertTrue(_in is not rst, 'result must not be input')
