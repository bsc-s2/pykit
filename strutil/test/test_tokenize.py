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


class TestTokenize(unittest.TestCase):

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
