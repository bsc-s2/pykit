#! /usr/bin/env python2
# coding: utf-8

import unittest
import datetime

from pykit import utfyaml
from pykit import ututil

dd = ututil.dd


class TestUtfyaml(unittest.TestCase):

    def test_load_scalar(self):

        cases = (
            (
                'hello, 中国',
                {},
                'hello, 中国',

                'test load string',
            ),

            (
                'hello, 中国',
                {
                    'encoding': None,
                },
                u'hello, 中国',

                'test load string and output with unicode',
            ),

            (
                '123',
                {},
                123,

                'test load number',
            ),

            (
                '3.14',
                {},
                3.14,

                'test load float',
            ),

            (
                'True',
                {},
                True,

                'test load bool',
            ),

            (
                '2018-04-17t15:09:43.10+08:00',
                {},
                datetime.datetime(2018, 4, 17, 7, 9, 43, 100000),

                'test load datetime object',
            ),

            (
                "!!python/unicode 'hello'",
                {},
                u'hello',

                'test load tag',
            ),
        )

        for src, kwargs, expected, msg in cases:

            self._test_yaml(utfyaml.load, src, expected, msg, **kwargs)


    def test_load_list(self):

        cases = (
            (
                '[猫, mouse, 狗]',
                {},
                ['猫', 'mouse', '狗'],

                'test normal load list',
            ),

            (
                '[猫, mouse, 狗]',
                {
                    'encoding': None,
                },
                [u'猫', u'mouse', u'狗'],

                'test normal load list and load str as unicode',
            ),

            (
                (
                    '- 猫\n'
                    '- mouse\n'
                    '- 狗\n'
                    '- goldfish\n'
                ),
                {},
                ['猫', 'mouse', '狗', 'goldfish'],

                'test load list with "-" style',
            ),

            (
                (
                    '- 猫\n'
                    '- mouse\n'
                    '- 狗\n'
                    '- goldfish\n'
                ),
                {
                    'encoding': None,
                },
                [u'猫', u'mouse', u'狗', u'goldfish'],

                'test load list with "-" style and load str as unicode',
            ),

            (
                '[1, two, 三, true, 3.14]',
                {},
                [1, 'two', '三', True, 3.14],

                'test load mixed'
            ),

            (
                '[1, two, 三]',
                {
                    'encoding': None,
                },
                [1, u'two', u'三'],

                'test load mixed and load str as unicode',
            ),

            (
                "[!!python/unicode 'hello', !!python/tuple ['tuple', 'value']]",
                {},
                [u'hello', ('tuple', 'value')],

                'test load list with tag',
            ),
        )

        for src, kwargs, expected, msg in cases:

            self._test_yaml(utfyaml.load, src, expected, msg, **kwargs)


    def test_load_dict(self):

        cases = (
            (
                (
                    'number: 1\n'
                    'string: hello\n'
                    'bool: [True, False]\n'
                    '汉字: 我\n'
                    "!!python/unicode 'unicode': !!python/unicode 'hello'\n"
                    "!!python/tuple [tuple, key]: !!python/tuple [tuple, value]\n"
                ),
                {},
                {
                    'number': 1,
                    'string': 'hello',
                    'bool': [True, False],
                    '汉字': '我',
                    u'unicode': u'hello',
                    ('tuple', 'key'): ('tuple', 'value'),
                },

                'test normal load dict',
            ),

            (
                (
                    'number: 1\n'
                    'string: hello\n'
                    'bool: [True, False]\n'
                    '汉字: 我\n'
                ),
                {
                    'encoding': None,
                },
                {
                    u'number': 1,
                    u'string': u'hello',
                    u'bool': [True, False],
                    u'汉字': u'我',
                },

                'test load dict and load str as unicode'
            ),

            (
                (
                    u'中国:\n'
                    u'  北京:\n'
                    u'    - 朝阳\n'
                    u'    - 海淀\n'
                ),
                {},
                {
                    '中国': {
                        '北京': ['朝阳', '海淀'],
                    },
                },

                'test load dict with indentation'
            ),

            (
                (
                    u'中国:\n'
                    u'  北京:\n'
                    u'    - 朝阳\n'
                    u'    - 海淀\n'
                ),
                {
                    'encoding': None,
                },
                {
                    u'中国': {
                        u'北京': [u'朝阳', u'海淀'],
                    },
                },

                'test load dict with indentation and load str as unicode'
            ),

            (
                '{hash: { name: Steve, foo: bar}}',
                {},
                {
                    'hash': {
                        'name': 'Steve',
                        'foo': 'bar',
                    },
                },

                'test load dict with "{}" style'
            ),

            (
                '{hash: { name: Steve, foo: bar}}',
                {
                    'encoding': None,
                },
                {
                    u'hash': {
                        u'name': u'Steve',
                        u'foo': u'bar',
                    },
                },

                'test load dict with "{}" style and load str as unicode'
            ),
        )

        for src, kwargs, expected, msg in cases:

            self._test_yaml(utfyaml.load, src, expected, msg, **kwargs)


    def test_dump_scalar(self):

        cases = (
            (
                'hello, 中国',
                {},
                'hello, 中国\n',

                'test normal dump scalar',
            ),

            (
                'hello, 中国',
                {
                    'encoding': None,
                },
                u'hello, 中国\n',

                'test output with unicode',
            ),

            (
                'hello, 中国',
                {
                    'encoding': 'GBK',
                },
                'hello, \xd6\xd0\xb9\xfa\n',

                'test output with GBK',
            ),

            (
                u'hello, 中国',
                {
                    'save_unicode': True,
                },
                "!!python/unicode 'hello, 中国'\n",

                'test output with utf-8 and save unicode as a object',
            ),

            (
                u'hello, 中国',
                {
                    'encoding': None,
                    'save_unicode': True,
                },
                u"!!python/unicode 'hello, 中国'\n",

                'test output with unicode and save unicode as a object',
            ),

            (
                u'hello, 中国',
                {
                    'encoding': 'GBK',
                    'save_unicode': True,
                },
                "!!python/unicode 'hello, \xd6\xd0\xb9\xfa'\n",

                'test output with unicode and save unicode as a object',
            ),

            (
                True,
                {},
                'true\n',

                'test dump bool',
            ),

            (
                123,
                {},
                '123\n',

                'test dump number',
            ),

            (
                3.14,
                {},
                '3.14\n',

                'test dump float',
            ),

            (
                datetime.datetime(2018, 7, 17),
                {},
                '2018-07-17 00:00:00\n',

                'test dump datetime object'
            ),
        )

        for src, kwargs, expected, msg in cases:

            self._test_yaml(utfyaml.dump, src, expected, msg, **kwargs)


    def test_dump_list(self):

        cases = (

            (
                ['猫', 'mouse', '狗'],
                {},
                '[猫, mouse, 狗]\n',

                'test normal dump list',
            ),

            (
                ['猫', 'mouse', '狗'],
                {
                    'encoding': None,
                },
                u'[猫, mouse, 狗]\n',

                'test output with unicode',
            ),

            (
                ['猫', 'mouse', '狗'],
                {
                    'encoding': 'GBK',
                },
                '[\xc3\xa8, mouse, \xb9\xb7]\n',

                'test output with GBK',
            ),

            (
                [u'猫', u'and', u'老鼠'],
                {
                    'save_unicode': True,
                },
                "[!!python/unicode '猫', !!python/unicode 'and', !!python/unicode '老鼠']\n",

                'test output with utf-8 and save unicode as object',
            ),

            (
                [u'猫', u'mouse', u'狗'],
                {
                    'encoding': 'GBK',
                    'save_unicode': True,
                },
                "[!!python/unicode '\xc3\xa8', !!python/unicode 'mouse', !!python/unicode '\xb9\xb7']\n",

                'test output with GBK and save unicode as object',
            ),
        )

        for src, kwargs, expected, msg in cases:

            self._test_yaml(utfyaml.dump, src, expected, msg, **kwargs)


    def test_dump_dict(self):

        src = {
            0: 'number key',

            'China': {
                'Captial': '北京',
                'Language': '普通话',
            },

            'bool': True,
            'number': 1,
            'string': 'hello',
            u'unicode': u'hello, 中文',
            '汉字': '我',

            ('tuple', 'key'): ('tuple', 'value'),
        }

        cases = (
            (
                {},
                (
                    '0: number key\n'
                    'China: {Captial: 北京, Language: 普通话}\n'
                    'string: hello\n'
                    'unicode: hello, 中文\n'
                    '汉字: 我\n'
                    'bool: true\n'
                    '? !!python/tuple [tuple, key]\n'
                    ': !!python/tuple [tuple, value]\n'
                    'number: 1\n'
                ),

                'normal test dump dict'
            ),

            (
                {
                    'encoding': None,
                },
                (
                    u'0: number key\n'
                    u'China: {Captial: 北京, Language: 普通话}\n'
                    u'string: hello\n'
                    u'unicode: hello, 中文\n'
                    u'汉字: 我\n'
                    u'bool: true\n'
                    u'? !!python/tuple [tuple, key]\n'
                    u': !!python/tuple [tuple, value]\n'
                    u'number: 1\n'
                ),

                'test output with unicode'
            ),

            (
                {
                    'encoding': 'GBK',
                },
                (
                    '0: number key\n'
                    'China: {Captial: \xb1\xb1\xbe\xa9, Language: \xc6\xd5\xcd\xa8\xbb\xb0}\n'
                    'string: hello\n'
                    'unicode: hello, \xd6\xd0\xce\xc4\n'
                    '\xba\xba\xd7\xd6: \xce\xd2\n'
                    'bool: true\n'
                    '? !!python/tuple [tuple, key]\n'
                    ': !!python/tuple [tuple, value]\n'
                    'number: 1\n'
                ),

                'test output with GBK'
            ),

            (
                {
                    'save_unicode': True,
                },
                (
                    '0: number key\n'
                    'China: {Captial: 北京, Language: 普通话}\n'
                    'string: hello\n'
                    "!!python/unicode 'unicode': !!python/unicode 'hello, 中文'\n"
                    '汉字: 我\n'
                    'bool: true\n'
                    '? !!python/tuple [tuple, key]\n'
                    ': !!python/tuple [tuple, value]\n'
                    'number: 1\n'
                ),

                'test output with utf-8 and save unicode as a object'
            ),

            (
                {
                    'encoding': 'GBK',
                    'save_unicode': True,
                },
                (
                    '0: number key\n'
                    'China: {Captial: \xb1\xb1\xbe\xa9, Language: \xc6\xd5\xcd\xa8\xbb\xb0}\n'
                    'string: hello\n'
                    "!!python/unicode 'unicode': !!python/unicode 'hello, \xd6\xd0\xce\xc4'\n"
                    '\xba\xba\xd7\xd6: \xce\xd2\n'
                    'bool: true\n'
                    '? !!python/tuple [tuple, key]\n'
                    ': !!python/tuple [tuple, value]\n'
                    'number: 1\n'
                ),

                'test output with GBK and save unicode as a object'
            ),
        )

        for kwargs, expected, msg in cases:

            self._test_yaml(utfyaml.dump, src, expected, msg, **kwargs)


    def _test_yaml(self, _exec, src, expected, msg, **kwargs):

            dd('msg: ', msg)
            dd('expected: ', expected)

            rst = _exec(src, **kwargs)

            dd('result  : ', rst)

            self.assertEqual(expected, rst)
