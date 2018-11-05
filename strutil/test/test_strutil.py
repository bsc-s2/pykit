#!/usr/bin/env python2
# coding: utf-8

import os
import unittest

from pykit import proc
from pykit import strutil
from pykit import ututil

dd = ututil.dd

this_base = os.path.dirname(__file__)
print this_base


def dd_lines(lines):
    dd()
    for l in lines:
        dd(l)


class TestStrutil(unittest.TestCase):

    def test_tokenize(self):

        base_cases = (
            ('', [''], ''),
            ('a', ['a'], ''),
            ('a b', ['a', 'b'], ''),
            (' a', ['', 'a'], ''),
            ('b ', ['b', ''], ''),
            ('abc def gh', ['abc', 'def', 'gh'], ''),
            ('"ab cd"', ['"ab cd"'], ''),
            ('"ab  cd"', ['"ab  cd"'], 'multiple space inside quotes'),
            ('"ab cd" ', ['"ab cd"', ''], ''),
            (' "ab cd"', ['', '"ab cd"'], ''),
            ('"ab cd" "x', ['"ab cd"'], 'discard incomplete'),
            ('"ab cd" "x y"', ['"ab cd"', '"x y"'], ''),

            ('foo "ab cd" "x y"', ['foo', '"ab cd"', '"x y"'], ''),
            ('foo "ab cd" "x', ['foo', '"ab cd"'], 'discard incomplete'),

            ('foo "\\"ab cd" "x', ['foo', '""ab cd"'], 'escape "'),
            ('foo "\\\\"ab cd" "x', ['foo', '"\\"ab', 'cd" "x'], 'escape \\'),
            ('foo "\\\\\\"ab cd" "x', ['foo', '"\\"ab cd"'], 'escape \\ "'),

            ('a \\"bc "d e" "f',  ['a', '"bc', '"d e"'], ''),
            ('a \\\\"bc "d e" "f',  ['a', '\\"bc "d', 'e" "f'], ''),
            ('a \\\\\\"bc "d e" "f',  ['a', '\\"bc', '"d e"'], ''),

            ('a "bc "d \\"f',  ['a', '"bc "d', '"f'], ''),
            ('a "bc "d \\\\"f',  ['a', '"bc "d'], ''),
            ('a "bc "d \\\\\\"f',  ['a', '"bc "d', '\\"f'], ''),

            ('\\"bc "d "f',  ['"bc', '"d "f'], ''),
            ('\\\\"bc "d "f',  ['\\"bc "d'], ''),
            ('\\\\\\"bc "d "f',  ['\\"bc', '"d "f'], ''),

            ('a "bc "d f\\"',  ['a', '"bc "d', 'f"'], ''),
            ('a "bc "d f\\\\"',  ['a', '"bc "d'], ''),
            ('a "bc "d f\\\\\\"',  ['a', '"bc "d', 'f\\"'], ''),
        )

        for _in, _out, _mes in base_cases:
            rst = strutil.tokenize(_in, sep=' ', preserve=True)
            self.assertEqual(_out, rst,
                             ('input: {_in}, output: {_out}, expected: {rst},'
                              ' message: {_mes}').format(
                                 _in=repr(_in),
                                 _out=repr(_out),
                                 rst=repr(rst),
                                 _mes=_mes
                             ))

        sep_cases = (
            ('',              None,    True,   []),
            (' a  b  c ',     None,    True,   ['a', 'b', 'c']),
            (' a  "b  c" ',   None,    True,   ['a', '"b  c"']),
            (' a  "b  c" ',   None,    False,  ['a', 'b  c']),
            ('a b c',         None,    True,   ['a', 'b', 'c']),
            ('"a b c"',       None,    True,   ['"a b c"']),
            ('"a b c"',       None,    False,  ['a b c']),
            ('a b"c d"',      None,    True,   ['a', 'b"c d"']),
            ('a b"c d"',      None,    False,  ['a', 'bc d']),
            ('a bcd',         'bc',    True,   ['a ', 'd']),
            ('a "bc" d',      'bc',    True,   ['a "bc" d']),
            ('a "bc" d',      'bc',    False,  ['a bc d']),
            ('abcd',          'abcd',  True,   ['', '']),
        )

        for line, sep, preserve, rst_expected in sep_cases:
            dd('in: ', line, sep)
            rst = strutil.tokenize(line, sep=sep, quote='"', preserve=preserve)
            dd('out: ', rst)
            self.assertEqual(rst, rst_expected)

        preserve_cases = (
            ('""',                   '"',    True,    ['""']),
            ('""',                   '"',    False,   ['']),
            ('abc xd efx gh',        'x',    True,    ['abc', 'xd efx', 'gh']),
            ('abc xd efx gh',        'x',    False,   ['abc', 'd ef', 'gh']),
            ('ab cxd efx gh',        'x',    True,    ['ab', 'cxd efx', 'gh']),
            ('ab cxd efx gh',        'x',    False,   ['ab', 'cd ef', 'gh']),
            ('ab cxd efxgh',         'x',    True,    ['ab', 'cxd efxgh']),
            ('ab cxd efxgh',         'x',    False,   ['ab', 'cd efgh']),
            ('ab cxd yey fx gh',     'xy',   True,    ['ab', 'cxd yey fx', 'gh']),
            ('ab cxd yey fx gh',     'xy',   False,   ['ab', 'cd yey f', 'gh']),
            ('ab cxd yey f gh',      'xy',   True,    ['ab']),
            ('ab cxd yey f gh',      'xy',   False,   ['ab']),
            ('ab cxd xex f gh',      'x',    True,    ['ab']),
            ('ab cxd xex f gh',      'x',    False,   ['ab']),
        )

        for line, quote, preserve, rst_expected in preserve_cases:
            dd('in: ', line, quote, preserve)
            rst = strutil.tokenize(line, sep=' ', quote=quote, preserve=preserve)
            dd('out: ', rst)
            self.assertEqual(rst, rst_expected)

    def test_parse_colon_kvs(self):
        cases = (
            ("abc:123", {'abc': '123'}),
            (" abc:123", {'abc': '123'}),
            ("abc:123 ", {'abc': '123'}),
            (" abc:123 ", {'abc': '123'}),
            ("    abc:123", {'abc': '123'}),
            ("abc:123   ", {'abc': '123'}),
            ("    abc:123   ", {'abc': '123'}),
            (" 'a:' bc:123", {'a': '', 'bc': '123'}),
            ("abc: '123:' ", {'abc': '', '123': ''}),
            ('a:bc:123', {'a': 'bc:123'}),
            ('abc:1:23', {'abc': '1:23'}),
            ('abc:\n123:', {'abc': '', '123': ''}),
            ('abc:\n123:\t', {'abc': '', '123': ''}),
            ('abc:\n\t123:', {'abc': '', '123': ''}),
            ("abc:123 abc:456", {'abc': '456'}),
            ("abc:123 def:456", {'abc': '123', 'def': '456'}),
            ("", {}),
            (":", {'': ''}),
            ("::", {'': ':'}),
        )

        for case, exp in cases:
            self.assertEqual(strutil.parse_colon_kvs(case), exp)

    def test_raise_value_error(self):
        cases = (
            "abc123",
            "abc:1 23",
            "abc: 123",
            "abc:   123",
        )

        for case in cases:
            self.assertRaises(ValueError, strutil.parse_colon_kvs, case)

    def test_common_prefix_invalid_arg(self):
        cases = (
            (1, []),
            ('a', 1),
            ('a', True),
            ('a', ('a',)),
            (('a', (),), ('a', 2,)),
        )

        for a, b in cases:
            dd('wrong type: ', repr(a), ' ', repr(b))
            self.assertRaises(TypeError, strutil.common_prefix, a, b)

    def test_common_prefix(self):
        cases = (
            ('abc',
             'abc',
             ),
            ('',
             '',
             '',
             ),
            ((),
             (),
             (),
             (),
             ),
            ('abc',
             'ab',
             'ab',
             ),
            ('ab',
             'abd',
             'ab',
             ),
            ('abc',
             'abd',
             'ab',
             ),
            ('abc',
             'def',
             '',
             ),
            ('abc',
             '',
             '',
             ),
            ('',
             'def',
             '',
             ),
            ('abc',
             'abd',
             'ag',
             'a',
             ),
            ('abc',
             'abd',
             'ag',
             'yz',
             '',
             ),
            ((1, 2,),
             (1, 3,),
             (1,),
             ),
            ((1, 2,),
             (2, 3,),
             (),
             ),
            ((1, 2, 'abc', ),
             (1, 2, 'abd', ),
             (1, 2, 'ab', ),
             ),
            ((1, 2, 'abc', ),
             (1, 2, 'xyz', ),
             (1, 2, ),
             ),
            ((1, 2, (5, 6), ),
             (1, 2, (5, 7), ),
             (1, 2, (5,), ),
             ),
            (('abc', '45',),
             ('abc', '46', 'xyz'),
             ('abc', '4',),
             ),
            (('abc', ('45', 'xyz'), 3),
             ('abc', ('45', 'xz'), 5),
             ('abc', ('45', 'x-'), 5),
             ('abc', ('45', 'x'),),
             ),
            (('abc', ('45', 'xyz'), 3),
             ('abc', ('45', 'xz'), 5),
             ('abc', ('x',),),
             ('abc',),
             ),
            ([1, 2, 3],
             [1, 2, 4],
             [1, 2],
             ),
        )

        for args in cases:
            expected = args[-1]
            args = args[:-1]

            dd('input: ', args, 'expected: ', expected)
            rst = strutil.common_prefix(*args)
            dd('rst: ', rst)

            self.assertEqual(expected, rst)

    def test_common_prefix_no_recursive(self):

        cases = (
            (('abc', ('45', 'xyz'), 3),
             ('abc', ('45', 'xz'), 5),
             ('abc', ('45', 'x-'), 5),
             ('abc',),
             ),
            ('abc',
             'abd',
             'ag',
             'a',
             ),
            ((1, 2, 'abc'),
             (1, 2, 'abd'),
             (1, 2),
             ),
        )

        for args in cases:
            expected = args[-1]
            args = args[:-1]

            dd('input: ', args, 'expected: ', expected)
            rst = strutil.common_prefix(*args, recursive=False)
            dd('rst: ', rst)

            self.assertEqual(expected, rst)

    def test_line_pad(self):

        cases = (
                (('', ''),
                 '',
                 ''
                 ),
                (('a', ''),
                 'a',
                 ''
                 ),
                (('a', ' '),
                 ' a',
                 ''
                 ),
                (('a', '   '),
                 '   a',
                 ''
                 ),
                (('a\nb', '   '),
                 '   a\n'
                 '   b',
                 ''
                 ),
                (('a\nbc', lambda line: 'x' * len(line)),
                 'xa\n'
                 'xxbc',
                 ''
                 ),
        )

        for _in, _out, _mes in cases:
            rst = strutil.line_pad(*_in)
            self.assertEqual(_out, rst,
                             ('input: {_in}, output: {_out}, expected: {rst},'
                              ' message: {_mes}').format(
                                 _in=repr(_in),
                                 _out=repr(_out),
                                 rst=repr(rst),
                                 _mes=_mes
                             ))

    def test_format_line(self):

        cases = (
                (([], '', ''),
                 '',
                 ''
                 ),
                ((['a'], '', ''),
                 'a',
                 ''
                 ),
                (([['a', 'bc']], '', ''),
                 ' a\n'
                 'bc',
                 'default alignment is to right'
                 ),
                (([['a', 'bc'], 'foo'], '', ''),
                 ' afoo\n'
                 'bc   ',
                 'no sep, add space to align'
                 ),
                (([['a', 'bc'], 'foo'], '|', ''),
                 ' a|foo\n'
                 'bc|   ',
                 'sep is "|"'
                 ),
                (([['a', 'bc'], 'foo', [1, 2, 333]], '|', ''),
                 ' a|foo|  1\n'
                 'bc|   |  2\n'
                 '  |   |333',
                 'number will be convert to str'
                 ),
                (([['a', 'bc'], 'foo', [1, 2, strutil.blue('xp')]], '|', ''),
                 ' a|foo| 1\n'
                 'bc|   | 2\n'
                 '  |   |' + str(strutil.blue('xp')),
                 'strutil.ColoredString instance is compatible'
                 ),
        )

        for _in, _out, _mes in cases:

            rst = strutil.format_line(*_in)

            dd("_in: " + str(_in))
            dd("rst:\n" + rst)

            self.assertEqual(_out, rst,
                             ('input: {_in}, output: {_out}, expected: {rst},'
                              ' message: {_mes}').format(
                                 _in=repr(_in),
                                 _out=repr(_out),
                                 rst=repr(rst),
                                 _mes=_mes
                             ))

    def test_struct_repr(self):

        inp = {
            1: 3,
            'x': {1: 4, 2: 5},
            'yyy': [1, 2, 3, 1000],
        }

        rst = strutil.struct_repr(inp)

        for l in rst:
            dd(repr(l))

        expected = [
            '  1 : 3     ',
            '  x : 1 : 4 ',
            '      2 : 5 ',
            'yyy : - 1   ',
            '      - 2   ',
            '      - 3   ',
            '      - 1000',
        ]

        self.assertEqual(expected, rst)

    def test_format_table(self):

        inp = [
            {'acl': {},
             'bucket': 'game1.read',
             'bucket_id': '1400000000000689036\000',
             'num_used': '0',
             'owner': 'game1',
             'space_used': '0',
             'ts': '1492091893065708032'},
            {'acl': {},
             'bucket': 'game2.read',
             'bucket_id': '1510000000000689037',
             'num_used': '0',
             'owner': 'game2',
             'space_used': '0',
             'ts': '1492091906629786880'},
            {'acl': {'imgx': ['READ', 'READ_ACP', 'WRITE', 'WRITE_ACP']},
             'bucket': 'imgx-test',
             'bucket_id': '1910000000000689048',
             'num_used': '0',
             'owner': 'imgx',
             'space_used': '0',
             'ts': '1492101189213795840'}]

        # default
        rst = strutil.format_table(inp)
        dd_lines(rst)

        # the last line is a '\n' splitted multi-row line
        expected = [
            'acl:               | bucket:    | bucket_id:          | num_used:  | owner:  | space_used:  | ts:                ',
            '{}                 | game1.read | 1400000000000689036 | 0          | game1   | 0            | 1492091893065708032',
            '{}                 | game2.read | 1510000000000689037 | 0          | game2   | 0            | 1492091906629786880',
            'imgx : - READ      | imgx-test  | 1910000000000689048 | 0          | imgx    | 0            | 1492101189213795840\n'
            '       - READ_ACP  |            |                     |            |         |              |                    \n'
            '       - WRITE     |            |                     |            |         |              |                    \n'
            '       - WRITE_ACP |            |                     |            |         |              |                    ',
        ]
        self.assertEqual(expected, rst)

        # specify key to render

        rst = strutil.format_table(inp, keys=[['bucket', 'B']])
        dd_lines(rst)
        expected = [
            'B:        ',
            'game1.read',
            'game2.read',
            'imgx-test ',
        ]
        self.assertEqual(expected, rst)

        # row_sep
        rst = strutil.format_table(inp, keys=['bucket'], row_sep='+')
        dd_lines(rst)
        expected = [
            'bucket:   ',
            '++++++++++',
            'game1.read',
            '++++++++++',
            'game2.read',
            '++++++++++',
            'imgx-test ',
        ]
        self.assertEqual(expected, rst)

        # sep
        rst = strutil.format_table(
            inp, keys=['bucket', 'bucket_id'], sep=' # ')
        dd_lines(rst)
        expected = [
            'bucket:    # bucket_id:         ',
            'game1.read # 1400000000000689036',
            'game2.read # 1510000000000689037',
            'imgx-test  # 1910000000000689048',
        ]
        self.assertEqual(expected, rst)

    def test_filter_invisible_chars(self):
        cases = (
            ("1273883926293937729\000\001\031", "1273883926293937729"),
            ("\x00\x01\x02\x03\x04\005", ""),
            (u"1122299299299299292", u"1122299299299299292"),
            (u"\x00\x01\x02\x03\x04\005", u""),
            (None, None),
            ("", "")
        )

        for case, expected in cases:
            self.assertEqual(
                expected, strutil.filter_invisible_chars(case))

    def test_utf8str(self):
        cases = (
                ('', ''),
                ('1', '1'),
                (1, '1'),
                (u'我', '\xe6\x88\x91'),
                ('\xe6\x88\x91', '\xe6\x88\x91'),
        )

        for inp, expected in cases:

            rst = strutil.utf8str(inp)

            self.assertEqual(expected, rst)

    def test_break_line(self):
        case = [
            ('a quick brown fox jumps over the lazy dog',        13,
             ['a quick brown', 'fox jumps', 'over the lazy', 'dog']),
            ('a quick\nbrown fox jumps over the lazy dog',       13,
             ['a quick', 'brown fox', 'jumps over', 'the lazy dog']),
            ('a quick\rbrown fox jumps over the lazy dog',       13,
             ['a quick', 'brown fox', 'jumps over', 'the lazy dog']),
            ('a quick brown fox jumps\r\nover the lazy dog',     13,
             ['a quick brown', 'fox jumps', 'over the lazy', 'dog']),
            ('a quick\nbrown\rfox jumps\r\nover the lazy dog',   13,    [
             'a quick', 'brown', 'fox jumps', 'over the lazy', 'dog']),
            ('aquickbrownfoxjumpsoverthelazydog',                9,     ['aquickbrownfoxjumpsoverthelazydog']),
            ('aquickbro',                                        9,     ['aquickbro']),
            (' aquickbro',                                       9,     ['', 'aquickbro']),
            ('  aquickbro',                                      9,     [' ', 'aquickbro']),
            ('aquickbro ',                                       9,     ['aquickbro']),
            ('aquickbro  ',                                      9,     ['aquickbro', ' ']),
            ('aqu ick br',                                       9,     ['aqu ick', 'br']),
            ('aqu ick br',                                       9.34,  ['aqu ick', 'br']),
            ('apu   ick  br',                                    5,     ['apu  ', 'ick ', 'br']),
            ('aqu ick br',                                       0,     ['aqu', 'ick', 'br']),
            ('aqu ick br',                                       -1,    ['aqu', 'ick', 'br']),
            ('',                                                 2,     []),
            (' ',                                                2,     [' ']),
            ('  ',                                               2,     ['  ']),
            ('   ',                                              2,     ['  ']),
            ('    ',                                             2,     ['  ', ' ']),
        ]

        for linestr, width, expected in case:
            rst = strutil.break_line(linestr, width)
            dd('case: ', linestr, width, expected)
            dd('rst: ', rst)
            self.assertEqual(rst, expected)

        colored_string_cases = [
            ([('asd ', 'red'), ('fer ', 'blue'), ('fg', 'white')],
             8,
             [[('asd', 'red'), (' ', None), ('fer', 'blue')],  [('fg', 'white')]],
             'base test',
             ),

            ([('asd ', 'red'), ('fer ', 'blue'),  ('fg', 'white')],
             -1,
             [[('asd', 'red')], [('fer', 'blue')],  [('fg', 'white')]],
             'test width',
             ),

            ([('asd   ', 'red'), ('fer  ', 'blue'),  ('fg', 'white')],
             5,
             [[('asd', 'red'), (' ', None), (' ', None)],
              [('fer', 'blue'), (' ', None)], [('fg', 'white')]],
             'test consecutive blank spaces',
             ),

            ([('  asd', 'red'), (' fer', 'blue'), ('fg   ', 'white')],
             4,
             [[(' ', None)], [('asd', 'red')], [('fer', 'blue'), ('fg', 'white')],
              [(' ', None), (' ', None)]],
             'consecutive blank spaces in the end and beginning',
             ),

            ([('asd\n', 'red'), ('f er ', 'blue'),  ('fg', 'white')],
             5,
             [[('asd', 'red')], [('f', 'blue'), (' ', None), ('er', 'blue')], [('fg', 'white')]],
             'test line break',
             ),

            ([('', None)],
             2,
             [],
             'test empty string',
             ),
        ]

        for _in, width, expected, msg in colored_string_cases:
            dd('msg: ', msg)

            color_in = strutil.ColoredString('')
            for elt in _in:
                color_in += strutil.ColoredString(elt[0], elt[1])
            color_expected = []
            for l in expected:
                buf = strutil.ColoredString('')
                for elt in l:
                    buf += strutil.ColoredString(elt[0], elt[1])
                color_expected.append(buf)

            rst = strutil.break_line(color_in, width)

            dd('rst: ', rst)
            dd('expected: ', color_expected)
            self.assertEqual(rst, color_expected)


class TestPage(unittest.TestCase):

    def test_page_no_pager(self):

        returncode, out, err = proc.command('python2', 'page_it.py',
                                            # pager, control_char, max_lines
                                            ' '.join(['python2', 'raw_pager.py', '>']), '0', '2',
                                            '1',
                                            '2',
                                            cwd=this_base,
                                            )

        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual('1\n2\n', out)

    def test_page_use_pager(self):

        returncode, out, err = proc.command('python2', 'page_it.py',
                                            # pager, control_char, max_lines
                                            ' '.join(['python2', 'raw_pager.py', '>']), '0', '2',
                                            '1',
                                            '2',
                                            '3',
                                            cwd=this_base,
                                            )

        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual('> 1\n> 2\n> 3\n', out)
