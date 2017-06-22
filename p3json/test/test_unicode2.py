#!/usr/bin/env python2
# coding: utf-8

from collections import OrderedDict
from pykit.p3json.test import PyTest

from pykit import ututil

dd = ututil.dd


class TestS2Cases(object):

    def test_loads_dumps(self):

        cases = [
                ('""', ''),
                ('"it168/\xb6\xd4.exe"', 'it168/\xb6\xd4.exe'),
                ('"\xe6\x88\x91"', '我'),
        ]

        for json_str, obj in cases:

            mes = 'case json, object: ' + repr((json_str, obj))
            dd(mes)

            result = self.json.loads(json_str)
            self.assertEqual(obj, result)

            # XXX ensure_ascii=False: not to dump unicode as \uxxxx. Be compatible with lua cjson
            result = self.json.dumps(obj, ensure_ascii=False)
            self.assertEqual(json_str, result)

    def test_loads(self):

        cases = [
                ('"\\/\xb6\xd4."', '/\xb6\xd4.'),
                ('"\xe6\x88\x91"', '我'),

                # unicode is loaded and encoded in utf-8
                ('"abc\\u6211"', 'abc\xe6\x88\x91'),

                ('{"我": "我"}', {'我':'我'}),
                ('{"\\u6211": "\\u6211"}', {u'我'.encode('utf-8'): u'我'.encode('utf-8')}),
        ]

        for inp, expected in cases:

            mes = 'case load: json, object: ' + repr((inp, expected))
            dd(mes)

            result = self.json.loads(inp)
            dd('result:', repr(result))

            self.assertEqual(expected, result)

    def test_dumps(self):

        self.assertEqual('"\xe6\x88\x91"', self.json.dumps( '我', ensure_ascii=False))
        self.assertEqual('"\\u6211"',      self.json.dumps(u'我', ensure_ascii=True))
        self.assertEqual(u'"\u6211"',      self.json.dumps(u'我', ensure_ascii=False))
        self.assertEqual(str,              type(self.json.dumps(u'我', ensure_ascii=True)))
        self.assertEqual(str,              type(self.json.dumps( '我', ensure_ascii=False)))


class TestPyS2Cases(TestS2Cases, PyTest): pass
