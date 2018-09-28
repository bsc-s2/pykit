#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import strutil
from pykit import ututil

dd = ututil.dd


def dd_lines(lines):
    dd()
    for l in lines:
        dd(l)


class TestColoredString(unittest.TestCase):

    cs = strutil.ColoredString

    def test_colorize_input(self):

        cases = (
                (0, 0),

                (0, 1),
                (0, 100),
                (1, 100),
                (50, 100),
                (100, 100),

                (0, -1),
                (0, -100),
                (1, -100),
                (50, -100),
                (100, -100),
        )

        print

        for v, total in cases:
            print strutil.colorize(v, total, str(v) + '/' + str(total))

    def test_show_all_colors(self):

        for c in range(256):
            if c % 16 == 0:
                print
            print self.cs('{0:>3}'.format(c), c),

    def test_named_color(self):

        print

        # named color shortcuts
        print strutil.blue('blue'),
        print strutil.cyan('cyan'),
        print strutil.green('green'),
        print strutil.yellow('yellow'),
        print strutil.red('red'),
        print strutil.purple('purple'),
        print strutil.white('white'),
        print

        print strutil.danger('danger'),
        print strutil.warn('warn'),
        print strutil.loaded('loaded'),
        print strutil.normal('normal'),
        print strutil.optimal('optimal'),
        print

    def test_pading(self):

        print
        for i in range(0, 100, 5):
            print strutil.colorize(i, 100),
        print

        for i in range(0, 100, 5):
            print strutil.colorize(i, -100),
        print

    def test_length(self):

        cases = (
            '',
            'string',
            '幾時何時',
            '\xf3',
        )

        for v in cases:
            self.assertEqual(len(self.cs(v, 'warn')), len(v))

    def test_add(self):

        # concat colored string with '+', like normal string
        s = self.cs('danger', 'danger') + self.cs('warn', 'warn')
        self.assertEqual(len('danger' + 'warn'), len(s))

        s += 'extra_string'
        self.assertEqual(len('danger' + 'warn' + 'extra_string'), len(s))

    def test_mul(self):

        # colored string can be duplicated with '*', like normal string
        s = (self.cs('danger', 'danger')
             + self.cs('warn', 'warn')
             + self.cs(' normal')) * 3

        slen = len('danger' + 'warn' + ' normal') * 3
        self.assertEqual(slen, len(s))

        s *= 10
        slen *= 10
        self.assertEqual(slen, len(s))

    def test_rerender(self):

        print

        # re-render strutil.ColoredString
        s = 'danger rerender to warn'

        c = self.cs(s, 'danger')
        print 'colorize with "danger":', c

        c = self.cs(c, 'warn')
        print 'colorize with "warn"  :', c

    def test_colored_prompt(self):

        s = '[colored prompt]# '

        prompt = self.cs(s, color='optimal', prompt=True)
        not_prompt = self.cs(s, color='optimal', prompt=False)

        self.assertEqual(str(prompt)[0], '\001')
        self.assertEqual(str(prompt)[-1], '\002')
        self.assertEqual(len(str(prompt)), len(str(not_prompt)) + 4)

        prompt += 'whatever'
        not_prompt += 'whatever'
        self.assertEqual(len(str(prompt)), len(str(not_prompt)) + 4)

        prompt *= 3
        not_prompt *= 3
        self.assertEqual(len(str(prompt)), len(str(not_prompt)) + 4 * 3)

    def test_split(self):
        color_cases = [
            ([('asd ', 'red'), ('fer ', 'blue'),  ('fg', 'white')],
             (' ', 0),
             [[('asd ', 'red'), ('fer ', 'blue'),  ('fg', 'white')]],
             'test maxsplit 0',
             ),

            ([('asd ', 'red'), ('fer ', 'blue'),  ('fg', 'white')],
             (' ', 1),
             [[('asd', 'red')], [('fer ', 'blue'),  ('fg', 'white')]],
             'test maxsplit 1',
             ),

            ([('asd ', 'red'), ('fer ', 'blue'),  ('fg', 'white')],
             (' ', -1),
             [[('asd', 'red')], [('fer', 'blue')],  [('fg', 'white')]],
             'test maxsplit -1',
             ),

            ([('asdx', 'red'), ('yferx', 'blue'),  ('yfg', 'white')],
             ('xy', -1),
             [[('asd', 'red')], [('fer', 'blue')], [('fg', 'white')]],
             'diff color separator',
             ),

            ([('asdx', 'red'), ('yferx', 'blue'),  ('yfg', 'white')],
             ('xy', 1),
             [[('asd', 'red')], [('ferx', 'blue'), ('yfg', 'white')]],
             'diff color separator and maxsplit',
             ),

            ([('asdx', 'red'), ('yferx', 'blue'),  ('yfg', 'white')],
             ('xyz', -1),
             [[('asdx', 'red'), ('yferx', 'blue'), ('yfg', 'white')]],
             'no separator in ColoredString',
             ),

            ([('  asd ', 'red'), (' fer ', 'blue'),  (' fg ', 'white')],
             (None, -1),
             [[('asd', 'red')], [('fer', 'blue')], [('fg', 'white')]],
             'separator is None',
             ),

            ([('  asd ', 'red'), (' fer ', 'blue'),  (' fg ', 'white')],
             (None, 1),
             [[('asd', 'red')], [('fer ', 'blue'), (' fg ', 'white')]],
             'separator is None and test maxsplit',
             ),

            ([('  ', 'red'), (' \r', 'blue'), ('\n  ', 'white')],
             [None, -1],
             [],
             'whitespace string and separator is None',
             ),

            ([('  ', 'red'), (' \r', 'blue'), ('\n  ', 'white')],
             [' ', -1],
             [[('', 'red')], [('', 'red')], [('', 'red')],
              [('\r', 'blue'), ('\n', 'white')], [('', 'red')], [('', 'red')]],
             'consecutive separator string',
             ),

            ([('', 'red')],
             [' ', 1],
             [[('', None)]],
             'blank string',
             ),
        ]

        for _in, args, expected, msg in color_cases:
            dd('msg: ', msg)

            expect_rsts = []
            for elts in expected:
                cs = strutil.ColoredString('')
                for elt in elts:
                    cs += strutil.ColoredString(elt[0], elt[1])
                expect_rsts.append(cs)

            color_in = strutil.ColoredString('')

            for elt in _in:
                color_in += strutil.ColoredString(elt[0], elt[1])

            rst = color_in.split(*args)

            dd('rst: ', rst)
            dd('expected: ', expect_rsts)
            self.assertEqual(rst, expect_rsts)

    def test_splitlines(self):
        color_cases = [
            ([('asd\r', 'red'), ('fer\n', 'blue'),  ('fg\r\n', 'white')],
             [True],
             [[('asd\r', 'red')], [('fer\n', 'blue')], [('fg\r\n', 'white')]],
             'test keepend true',
             ),

            ([('asd\r', 'red'), ('fer\n', 'blue'),  ('fg\r\n', 'white')],
             [False],
             [[('asd', 'red')], [('fer', 'blue')], [('fg', 'white')]],
             'test keepend false',
             ),

            ([('asd\r', 'red'), ('\nfer', 'blue'),  ('fg', 'white')],
             [True],
             [[('asd\r', 'red'), ('\n', 'blue')], [('fer', 'blue'), ('fg', 'white')]],
             '\\r\\n in diff color and keepend',
             ),

            ([('asd\r', 'red'), ('\nfer', 'blue'),  ('fg', 'white')],
             [False],
             [[('asd', 'red')], [('fer', 'blue'), ('fg', 'white')]],
             '\\r\\n in diff color and not keepend',
             ),

            ([('\nasd\r', 'red'), ('\nfer', 'blue'),  ('fg\r\n', 'white')],
             [True],
             [[('\n', 'red')], [('asd\r', 'red'), ('\n', 'blue')], [
                 ('fer', 'blue'), ('fg\r\n', 'white')]],
             'line break at the start and the end and keepend',
             ),

            ([('\nasd\r', 'red'), ('\nfer', 'blue'),  ('fg\r\n', 'white')],
             [False],
             [[('', 'red')], [('asd', 'red')], [
                 ('fer', 'blue'), ('fg', 'white')]],
             'line break at the start and the end and not keepend',
             ),

            ([('\n', 'red'), ('\r\n', 'blue'), ('\r\n', 'white')],
             [True],
             [[('\n', 'red')], [('\r\n', 'blue')], [('\r\n', 'white')]],
             'colored string consisted of all line breaks and keepend',
             ),

            ([('\n', 'red'), ('\r\n', 'blue'), ('\r\n', 'white')],
             [False],
             [[('', 'red')], [('', 'blue')], [('', 'white')]],
             'colored string consisted of all line breaks and not keepend',
             ),

            ([('asd ', 'red'), ('fer ', 'blue'),  ('fg', 'white')],
             [True],
             [[('asd ', 'red'), ('fer ', 'blue'),  ('fg', 'white')]],
             'no line break',
             ),

            ([('', 'red')],
             [True],
             [],
             'blank string',
             ),
        ]

        for _in, args, expected, msg in color_cases:
            dd('msg: ', msg)

            expect_rsts = []
            for elts in expected:
                cs = strutil.ColoredString('')
                for elt in elts:
                    cs += strutil.ColoredString(elt[0], elt[1])
                expect_rsts.append(cs)

            color_in = strutil.ColoredString('')
            for elt in _in:
                color_in += strutil.ColoredString(elt[0], elt[1])

            rst = color_in.splitlines(*args)

            dd('rst: ', rst)
            dd('expected: ', expect_rsts)
            self.assertEqual(rst, expect_rsts)

    def test_join(self):
        string_case = [
            ('ab',

             [('x', 'red'), ('y', 'blue')],

             [('a', None), ('x', 'red'), ('y', 'blue'), ('b', None)],

             'string iter and string element',
             ),

            ({'a': 1, 'b': 2},

             [('x', 'red'), ('y', 'blue')],

             [('a', None), ('x', 'red'), ('y', 'blue'), ('b', None)],

             'dict iter and string element',
             ),

            (['a', 'b', 'c'],

             [('x', 'red'), ('y', 'blue')],

             [('a', None), ('x', 'red'), ('y', 'blue'), ('b', None), ('x', 'red'), ('y', 'blue'), ('c', None)],

             'list iter and string element',
             ),

            (['a', 'b', 'c'],

             [('', None)],

             [('a', None), ('b', None), ('c', None)],

             'no separator',
             ),

            (['a'],

             [(' ', None)],

             [('a', None)],

             'iter with just 1 element',
             ),

            ([],

             [(' ', None)],

             [],

             'iter with no element',
             ),

        ]

        for iterable, sep, expected, msg in string_case:
            dd('msg: ', msg)

            color_sep = strutil.ColoredString('')
            for elt in sep:
                color_sep += strutil.ColoredString(elt[0], elt[1])

            rst = color_sep.join(iterable)

            color_expected = strutil.ColoredString('')
            for elt in expected:
                color_expected += strutil.ColoredString(elt[0], elt[1])

            dd('rst: ', rst)
            dd('expected: ', color_expected)
            self.assertEqual(rst, color_expected)

        ColoredString_case = [
            ([[('a', 'red'), ('b', 'blue')]],

             [('x', 'red'), ('y', 'blue')],

             [('a', 'red'), ('b', 'blue')],

             '1 ColoredString element',
             ),

            ([[('a', 'red')], [('b', 'blue'), ('c', 'white')]],

             [('x', 'red'), ('y', 'blue')],

             [('a', 'red'), ('x', 'red'), ('y', 'blue'), ('b', 'blue'), ('c', 'white')],

             '2 ColoredString elements',
             ),

            (['a', [('b', 'blue'), ('c', 'white')], 'd'],

             [('x', 'red'), ('y', 'blue')],

             [('a', None), ('x', 'red'), ('y', 'blue'), ('b', 'blue'), ('c', 'white'),
                 ('x', 'red'), ('y', 'blue'), ('d', None)],

             'ColoredString and string',
             ),

            ([[('a', 'red')], [('b', 'blue'), ('c', 'white')]],

             [(' ', None)],

             [('a', 'red'), (' ', None), ('b', 'blue'), ('c', 'white')],

             'with colored blank space',
             ),

            ([[('a', 'red')], [('b', 'blue')], [('c', 'white')]],

             [('', None)],

             [('a', 'red'), ('b', 'blue'), ('c', 'white')],

             'with no separator',
             ),

            ([[(' ', 'red')], [(' ', 'blue')]],

             [(' ', 'white')],

             [(' ', 'red'), (' ', 'white'),  (' ', 'blue')],

             'colored blank space element with blank space separator',
             ),

        ]

        for _in, sep, expected, msg in ColoredString_case:
            dd('msg: ', msg)

            color_in = []
            for l in _in:
                if type(l) != type([]):
                    color_in.append(l)
                    continue

                cs = strutil.ColoredString('')
                for elt in l:
                    cs += strutil.ColoredString(elt[0], elt[1])
                color_in.append(cs)

            color_sep = strutil.ColoredString('')
            for elt in sep:
                color_sep += strutil.ColoredString(elt[0], elt[1])

            rst = color_sep.join(color_in)

            color_expected = strutil.ColoredString('')
            for elt in expected:
                color_expected += strutil.ColoredString(elt[0], elt[1])

            dd('rst: ', rst)
            dd('expected: ', color_expected)
            self.assertEqual(rst, color_expected)
