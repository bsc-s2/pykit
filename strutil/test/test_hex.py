#!/usr/bin/env python2
# coding: utf-8

import os
import unittest

from pykit import strutil
from pykit.strutil import Hex
from pykit import ututil
from pykit import utfjson

dd = ututil.dd


class TestHex(unittest.TestCase):

    def test_init(self):

        byte_length = 3

        cases = (
                (0, 0),
                ('000000', 0),
                ('\0\0\0', 0),

                (256**2 + 2*256 + 3, 0x010203),
                ('010203', 0x010203),
                ('\1\2\3', 0x010203),
        )

        for inp, expected in cases:
            dd(inp, expected)
            c = Hex(inp, byte_length)
            self.assertEqual(expected, c.int)
            self.assertEqual('%06x' % expected, c)

    def test_attr(self):
        c = Hex('010203', 3)
        self.assertEqual('010203', c.hex)
        self.assertEqual('\1\2\3', c.bytes)
        self.assertEqual(256**2 + 2*256 + 3, c.int)

        self.assertIs('010203', c.hex)
        self.assertIsNot('010203', c)

    def test_init_invalid(self):

        byte_length = 3

        cases = (
                (256**3-1,   None),
                (256**3,     ValueError),
                (-1,         ValueError),
                ('\1\2',     ValueError),
                ('\1\2\3\4', ValueError),
                ('0102',     ValueError),
                ('01020',    ValueError),
                ('0102030',  ValueError),
                ('01020304', ValueError),

                ({}, TypeError),
        )

        for inp, err in cases:
            dd(inp, err)
            if err is None:
                c = Hex(inp, byte_length)
            else:
                self.assertRaises(err, Hex, inp, byte_length)

    def test_named_length(self):
        val = 0x010203
        cases = (
            ('crc32',  '00010203'),
            ('Crc32',  '00010203'),
            ('CRC32',  '00010203'),
            ('md5',    '00000000000000000000000000010203'),
            ('Md5',    '00000000000000000000000000010203'),
            ('MD5',    '00000000000000000000000000010203'),
            ('sha1',   '0000000000000000000000000000000000010203'),
            ('Sha1',   '0000000000000000000000000000000000010203'),
            ('SHA1',   '0000000000000000000000000000000000010203'),
            ('sha256', '0000000000000000000000000000000000000000000000000000000000010203'),
            ('Sha256', '0000000000000000000000000000000000000000000000000000000000010203'),
            ('SHA256', '0000000000000000000000000000000000000000000000000000000000010203'),
        )

        for typ, expected in cases:
            c = Hex(val, typ)
            self.assertEqual(expected, c)

    def test_checksum_shortcut(self):
        val = 0x010203
        self.assertEqual(Hex(val, 'crc32'), Hex.crc32(val))
        self.assertEqual(Hex(val, 'md5'), Hex.md5(val))
        self.assertEqual(Hex(val, 'sha1'), Hex.sha1(val))
        self.assertEqual(Hex(val, 'sha256'), Hex.sha256(val))

    def test_prefix(self):

        pref = '1234'
        cases = (
            ('crc32',  '12340000'),
            ('md5',    '12340000000000000000000000000000'),
            ('sha1',   '1234000000000000000000000000000000000000'),
            ('sha256', '1234000000000000000000000000000000000000000000000000000000000000'),
        )

        for typ, expected in cases:
            dd('typ:', typ)

            c = Hex((pref, 0), typ)

            self.assertEqual(expected, c)

        self.assertEqual('12340101', Hex((pref, 1), 'crc32'))

    def test_str_repr(self):
        c = Hex.crc32(1)
        self.assertEqual('00000001', str(c))
        self.assertEqual("'00000001'", repr(c))

    def test_json(self):
        c = Hex.crc32(('0002', 0))
        rst = utfjson.dump(c)
        self.assertEqual('"00020000"', rst)
        self.assertEqual(c, utfjson.load(rst))

    def test_arithmetic(self):

        c = Hex.crc32(5)

        self.assertEqual(6,  (c+1).int)
        self.assertEqual(10, (c*2).int)
        self.assertEqual(2,  (c/2).int)
        self.assertEqual(0,  (c/6).int)
        self.assertEqual(1,  (c % 2).int)
        self.assertEqual(25, (c**2).int)

        self.assertEqual('00000006', (c+1))
        self.assertEqual('0000000a', (c*2))
        self.assertEqual('00000002', (c/2))
        self.assertEqual('00000000', (c/6))
        self.assertEqual('00000001', (c % 2))
        self.assertEqual('00000019', (c**2))

        self.assertEqual(6, (c + Hex.crc32(1)).int)

        # overflow protection

        self.assertEqual(0, (c-5).int)
        self.assertEqual(0, (c-6).int)

        d = Hex.crc32(('', 0xff))
        self.assertEqual(d, d+1)

    def test_arithmetic_error(self):

        c = Hex.crc32(5)
        cases = (
            [],
            (),
            {},
            'x',
            u'我',
        )

        for inp in cases:
            with self.assertRaises(TypeError):
                c + inp
            with self.assertRaises(TypeError):
                c - inp
            with self.assertRaises(TypeError):
                c * inp
            with self.assertRaises(TypeError):
                c / inp
            with self.assertRaises(TypeError):
                c % inp
            with self.assertRaises(TypeError):
                c ** inp
