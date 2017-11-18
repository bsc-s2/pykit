import types
import unittest

from pykit import humannum
from pykit import ututil

dd = ututil.dd


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

        for _in, _out, _msg in cases:

            rst = humannum.humannum(_in)

            msg = 'humanize: in: {_in} expect: {_out}, rst: {rst}; {_msg}'.format(
                _in=repr(_in),
                _out=repr(_out),
                rst=rst,
                _msg=_msg
            )

            self.assertEqual(_out, rst, msg)

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

        suffixes = (
            '',
            'b', 'i', 'ib',
            'B', 'I', 'iB',
        )

        for _in, _out, _msg in cases:

            rst = humannum.parsenum(_in)

            msg = 'parse: in: {_in} expect: {_out}, rst: {rst}; {_msg}'.format(
                _in=repr(_in),
                _out=repr(_out),
                rst=rst,
                _msg=_msg
            )

            self.assertEqual(_out, rst, msg)

            for suff in suffixes:

                dd('parseint:', _in, ' suffix: ', suff)
                self.assertEqual(int(_out), humannum.parseint(_in + suff),
                                 msg + '; parseint with suffix: ' + repr(suff))

    def test_parse_percentage(self):

        cases = (
                ('0%',           0,        ),
                ('-0%',          0,        ),
                ('1%',           0.01,     ),
                ('-1%',         -0.01,     ),
                ('1.00%',        0.01,     ),
                ('1.1%',         0.011,    ),
                ('100%',         1.0,      ),
                ('-100%',       -1.0,      ),
                ('100.1%',       1.001,    ),
                ('1200.123%',   12.00123,  ),
                ('-1200.123%', -12.00123,  ),
        )

        for _in, expected in cases:

            rst = humannum.parsenum(_in)

            msg = 'parse: in: {_in} expect: {expected}, rst: {rst}'.format(
                _in=repr(_in),
                expected=repr(expected),
                rst=repr(rst),
            )

            self.assertTrue(0.000000001 > expected - rst > -0.000000001, msg)

            self.assertEqual(int(expected), humannum.parseint(_in), 'int: ' + msg)

    def test_safe_parse(self):

        cases = (
                ('1%',    0.01,),
                ('1%x',   '1%x',),
                ('x1%x',  'x1%x',),
                ('1',     1,),
                ('1-',    '1-',),
                ('x1y',   'x1y',),
                ('1K',    1024,),
                ('1Kqq',  '1Kqq',),
                ('1.01',  1.01,),
                ('1..01', '1..01',),
        )

        for _in, expected in cases:

            rst = humannum.parsenum(_in, safe=True)

            msg = 'parse: in: {_in} expect: {expected}, rst: {rst}'.format(
                _in=repr(_in),
                expected=repr(expected),
                rst=repr(rst),
            )
            dd(msg)

            self.assertEqual(expected, rst)

            if not isinstance(expected, types.StringTypes):
                rst = humannum.parseint(_in, safe=True)
                self.assertEqual(int(expected), rst)

    def test_specified_unit(self):

        cases = (
                ((1024 ** 2, {'unit': 1024}),      '1024K',   ''),
                ((1024 ** 2, {'unit': 1024**3}),   '0.001G',  ''),
        )

        for _in, _out, _msg in cases:

            rst = humannum.humannum(_in[0], **_in[1])

            msg = 'in: {_in} expect: {_out}, rst: {rst}; {_msg}'.format(
                _in=repr(_in),
                _out=repr(_out),
                rst=rst,
                _msg=_msg
            )

            self.assertEqual(_out, rst, msg)

    def test_non_primitive(self):

        cases = (
                ({'a': 10240},              {'a': '10K'},              ''),
                ([{'a': 10240}, 1024432],   [{'a': '10K'}, '1000.4K'], ''),
                ([{'a': 'xp'},  1024432],   [{'a': 'xp'}, '1000.4K'], ''),
        )

        for _in, _out, _msg in cases:

            rst = humannum.humannum(_in)

            msg = 'in: {_in} expect: {_out}, rst: {rst}; {_msg}'.format(
                _in=repr(_in),
                _out=repr(_out),
                rst=rst,
                _msg=_msg
            )

            self.assertEqual(_out, rst, msg)
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

        for _in, _out, _msg in cases:

            rst = humannum.humannum(_in[0], **_in[1])

            msg = 'in: {_in} expect: {_out}, rst: {rst}; {_msg}'.format(
                _in=repr(_in),
                _out=repr(_out),
                rst=rst,
                _msg=_msg
            )

            self.assertEqual(_out, rst, msg)
            self.assertTrue(_in is not rst, 'result must not be input')

    def test_unit(self):

        self.assertEqual('', humannum.value_to_unit[1])

        cases = (
                (1024**1, 'K'),
                (1024**2, 'M'),
                (1024**3, 'G'),
                (1024**4, 'T'),
                (1024**5, 'P'),
                (1024**6, 'E'),
                (1024**7, 'Z'),
                (1024**8, 'Y'),
        )

        for inp, expected in cases:

            rst = humannum.value_to_unit[inp]
            self.assertEqual(expected, rst)

            rst = humannum.unit_to_value[expected]
            self.assertEqual(inp, rst)

            with self.assertRaises(KeyError):
                humannum.value_to_unit[inp + 1]

            with self.assertRaises(KeyError):
                humannum.value_to_unit[inp - 1]
