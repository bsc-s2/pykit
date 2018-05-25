#!/usr/bin/env python2.6
# coding: utf-8

import unittest

from pykit import utfjson


class TestUTFJson(unittest.TestCase):

    def test_load(self):

        self.assertEqual(None, utfjson.load(None))
        self.assertEqual({}, utfjson.load('{}'))

        # load unicode, result in utf-8

        self.assertEqual('我',      utfjson.load('"\\u6211"'))
        self.assertEqual(str,  type(utfjson.load('"\\u6211"')))

        # unicode and string in a dictionary.

        obj = '{"a": "\\u6211", "b": "1"}'
        rst = utfjson.load(obj)

        self.assertEqual({"a": "\xe6\x88\x91", "b": "1"}, rst)
        self.assertEqual(str, type(rst["a"]))
        self.assertEqual(str, type(rst["b"]))

        # load utf-8, result in str

        rst = utfjson.load('"\xe6\x88\x91"')
        self.assertEqual('我', rst)
        self.assertEqual(str,  type(rst))

        # load gbk, result in str, in gbk encoding

        gbk = '"\xb6\xd4\xd5\xbd\xc6\xbd\xcc\xa8\xb9\xd9\xb7\xbd\xd7\xee\xd0\xc2\xb0\xe6"'
        self.assertEqual('对战平台官方最新版'.decode('utf-8').encode('gbk'), utfjson.load(gbk))
        self.assertEqual(str, type(utfjson.load(gbk)))

        # load any

        s = '"\xbb"'
        rst = utfjson.load(s)
        self.assertEqual('\xbb', rst)
        self.assertEqual(str, type(rst))

    def test_load_backslash_x_encoded(self):

        s = '"\\x61"'
        self.assertEqual('a', utfjson.load(s))

        s = '"\\X61"'
        self.assertEqual('a', utfjson.load(s))

        s = '"\\xe6\\x88\\x91"'
        self.assertEqual('我', utfjson.load(s))

        self.assertRaises(utfjson.JSONDecodeError, utfjson.load, '"\\"')
        self.assertRaises(utfjson.JSONDecodeError, utfjson.load, '"\\x"')
        self.assertRaises(utfjson.JSONDecodeError, utfjson.load, '"\\x6"')

    def test_load_decode(self):
        self.assertEqual('我', utfjson.load('"我"'))
        self.assertEqual(u'我', utfjson.load('"我"', encoding='utf-8'))
        self.assertEqual(unicode, type(utfjson.load('"我"', encoding='utf-8')))

        self.assertEqual({'a': u"我".encode('utf-8')}, utfjson.load('{"a": "\\u6211"}'))
        self.assertEqual({'a': u"我"}, utfjson.load('{"a": "我"}', encoding='utf-8'))
        self.assertEqual({'a':  "我"}, utfjson.load('{"a": "我"}'))
        self.assertEqual({'a':  "我"}, utfjson.load('{"a": "我"}'))
        self.assertEqual(["我"],       utfjson.load('["我"]'))


    def test_dump(self):

        self.assertEqual('null', utfjson.dump(None))
        self.assertEqual('{}', utfjson.dump({}))

        self.assertRaises(TypeError, utfjson.dump, '我',      encoding=None)
        self.assertRaises(TypeError, utfjson.dump, {'我':1},  encoding=None)
        self.assertRaises(TypeError, utfjson.dump, {1:'我'},  encoding=None)
        self.assertRaises(TypeError, utfjson.dump, ['我'],    encoding=None)
        self.assertRaises(TypeError, utfjson.dump, [('我',)], encoding=None)

        self.assertEqual('"\\u6211"',      utfjson.dump(u'我', encoding=None))
        self.assertEqual('"\xb6\xd4"',     utfjson.dump(u'对', encoding='gbk'))
        self.assertEqual('"\xe6\x88\x91"', utfjson.dump(u'我', encoding='utf-8'))

        self.assertEqual('"\xe6\x88\x91"', utfjson.dump(u'我'))
        self.assertEqual('"\xe6\x88\x91"', utfjson.dump( '我'))

        # by default unicode are encoded

        self.assertEqual('{"\xe6\x88\x91": "\xe6\x88\x91"}', utfjson.dump({ "我":  "我"}))
        self.assertEqual('{"\xe6\x88\x91": "\xe6\x88\x91"}', utfjson.dump({ "我": u"我"}))
        self.assertEqual('{"\xe6\x88\x91": "\xe6\x88\x91"}', utfjson.dump({u"我":  "我"}))
        self.assertEqual('{"\xe6\x88\x91": "\xe6\x88\x91"}', utfjson.dump({u"我": u"我"}))
        self.assertEqual('["\xe6\x88\x91"]',                 utfjson.dump((u"我", )))

        self.assertEqual('{"\\u6211": "\\u6211"}', utfjson.dump({u"我": u"我"}, encoding=None))

        self.assertEqual('"\\""', utfjson.dump('"'))

        # encoded chars and unicode chars in one string
        self.assertEqual('/aaa\xe7\x89\x88\xe6\x9c\xac/jfkdsl\x01', utfjson.load('"\/aaa\xe7\x89\x88\xe6\x9c\xac\/jfkdsl\u0001"'))
