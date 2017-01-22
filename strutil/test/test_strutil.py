#!/usr/bin/env python2
# coding: utf-8

import inspect
import logging
import unittest

import strutil


class TestStrutil(unittest.TestCase):

    def test_tokenize(self):

        cases = (
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
        )

        for _in, _out, _mes in cases:
            rst = strutil.tokenize(_in)
            self.assertEqual(_out, rst,
                             ('input: {_in}, output: {_out}, expected: {rst},'
                              ' message: {_mes}').format(
                                 _in=repr(_in),
                                 _out=repr(_out),
                                 rst=repr(rst),
                                 _mes=_mes
                             ))

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

        logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__ + '.' + inspect.stack()[0][3])

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

            logger.debug("in: " + str(_in))
            logger.debug("rst:\n" + rst)

            self.assertEqual(_out, rst,
                             ('input: {_in}, output: {_out}, expected: {rst},'
                              ' message: {_mes}').format(
                                 _in=repr(_in),
                                 _out=repr(_out),
                                 rst=repr(rst),
                                 _mes=_mes
                             ))


class TestColoredString(unittest.TestCase):

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

        for v, total in cases:
            print strutil.colorize(v, total, str(v) + '/' + str(total))

    def test_all(self):

        print '--- colorized string ---'

        cc = strutil.ColoredString

        # list all fading color
        for i in range(0, 100, 5):
            print strutil.colorize(i, 100),
        print

        # concat colored string with '+', like normal string
        s = cc('danger', 'danger') + cc('warn', 'warn')
        self.assertEqual(len('danger' 'warn'), len(s))

        print s + 'jfksdl'

        # list all colors
        for c in range(256):
            if c % 16 == 0:
                print
            print cc('{0:>3}'.format(c), c),
        print

        # colored string can be duplicated with '*', like normal string
        p = (cc('danger', 'danger')
             + cc('warn', 'warn')
             + cc(' normal')) * 3
        plen = len('danger' 'warn' ' normal') * 3
        self.assertEqual(plen, len(p))
        print p
        print 'p*2:', p * 2

        # re-render strutil.ColoredString
        c = cc(p, 'warn')
        print 'colorize with "warn":', c
        print 'c*2:', c * 2
        self.assertEqual(plen, len(c), 'original c does not change after *')

        # no-color
        print 'de-colored:', cc(p)

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


# logging.basicConfig( stream=sys.stderr )
# logging.getLogger( __name__ + '.TestStrutil.test_format_line' ).setLevel( logging.DEBUG )
