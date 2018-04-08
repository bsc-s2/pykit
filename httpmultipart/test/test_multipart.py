#!/usr/bin/env python
#coding: utf-8

import unittest
import copy
import random
import string
import os

from pykit import httpmultipart
from pykit import fsutil

class TestMultipart(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestMultipart, self).__init__(*args, **kwargs)
        self.test_multipart = None

    def setUp(self):
        self.test_multipart = httpmultipart.Multipart()

    def test_headers(self):

        case = [
            [
                {
                    'Content-Length': 998,
                    'Content-Type': 'aaplication/octet-stream'
                },
                {
                    'Content-Length': 998,
                    'Content-Type': 'multipart/form-data; ' +
                        'boundary={b}'.format(b=self.test_multipart.boundary)
                }
            ],
            [
                {
                    'Content-Length': 1200
                },
                {
                    'Content-Length': 1200,
                    'Content-Type': 'multipart/form-data; ' +
                        'boundary={b}'.format(b=self.test_multipart.boundary)

                }
            ],
            [
                {
                    'Content-Type': 'application/octet-stream'
                },
                {
                    'Content-Length': 1335,
                    'Content-Type': 'multipart/form-data; ' +
                        'boundary={b}'.format(b=self.test_multipart.boundary)
                }
            ],
            [
                None,
                {
                    'Content-Length': 1335,
                    'Content-Type': 'multipart/form-data; ' +
                        'boundary={b}'.format(b=self.test_multipart.boundary)
                }
            ]
        ]

        str1 = '''
                使命：Better Internet ，Better life
                愿景：成为全球受人尊敬的科技公司；最具创新力；最佳雇主
                未来白山的特质：渴求变革；让创新超越客户想象；全球化；真诚、并始终如一
                信条：以用户为中心，其他一切水到渠成；专心将一件事做到极致；越快越好
               '''
        str2 = '''
                12343564343rfe
                fdf4erguu38788894hf
                12rfhfvh8876w91908777yfj
               '''
        str3 = '''
                838839938238838388383838
                dddjjdkkksijdidhdhhhhddd
                djdjdfdf4erguu38788894hf
                12rfhfvh8876w91908777yfj
               '''

        fsutil.write_file(
            '/tmp/a.txt', str1
        )
        fsutil.write_file(
            '/tmp/b.txt', str2
        )

        def make_file_reader():
            with open('/tmp/b.txt') as f:
                while True:
                    buf = f.read(1024 * 1024)
                    if buf == '':
                        break
                    yield buf

        def make_str_reader():
            yield str3

        str_reader = make_str_reader()
        str_size = len(str3)

        file_reader = make_file_reader()
        file_size = os.path.getsize('/tmp/b.txt')

        fields = [
            {
                'name': 'metadata1',
                'value': 'lvting',
                'headers': {'Date': 'Dec, 20 Dec 2018 15:00:00 GMT'}
            },
            {
                'name': 'metadata2',
                'value': [
                              open('/tmp/a.txt'),
                              os.path.getsize('/tmp/a.txt'),
                         ],
                'headers': {'Content-Type': 'application/octet-stream'}
            },
            {
                'name': 'metadata3',
                'value': [file_reader, file_size, 'b.txt'],
            },
            {
                'name': 'metadata4',
                'value': [str_reader, str_size],
            },
            {
                'name': 'metadata5',
                'value': ['234ffhhif3323jjfjf3']
            },
        ]
        for h in case:
            self.assertEqual(
                h[1],
                self.test_multipart.make_headers(fields, h[0])
            )
        fsutil.remove('/tmp/a.txt')
        fsutil.remove('/tmp/b.txt')

    def test_body(self):

        str1 = '''
                使命：Better Internet ，Better life
                愿景：成为全球受人尊敬的科技公司；最具创新力；最佳雇主
                未来白山的特质：渴求变革；让创新超越客户想象；全球化；真诚、并始终如一
                信条：以用户为中心，其他一切水到渠成；专心将一件事做到极致；越快越好
               '''
        str2 = '''
                12343564343rfe
                fdf4erguu38788894hf
                12rfhfvh8876w91908777yfj
               '''
        str3 = '''
                838839938238838388383838
                dddjjdkkksijdidhdhhhhddd
                djdjdfdf4erguu38788894hf
                12rfhfvh8876w91908777yfj
               '''

        fsutil.write_file(
            '/tmp/a.txt', str1
        )
        fsutil.write_file(
            '/tmp/b.txt', str2
        )

        def make_file_reader():
            with open('/tmp/b.txt') as f:
                while True:
                    buf = f.read(1024 * 1024)
                    if buf == '':
                        break
                    yield buf

        def make_str_reader():
            yield str3

        str_reader = make_str_reader()
        str_size = len(str3)

        file_reader = make_file_reader()
        file_size = os.path.getsize('/tmp/b.txt')

        case = [
            [
                [
                    {
                        'name': 'metadata1',
                        'value': 'lvting',
                        'headers': {'Date': 'Dec, 20 Dec 2018 15:00:00 GMT'}
                    }
                ],
                [
                    '--{b}'.format(b=self.test_multipart.boundary),
                    'Content-Disposition: form-data; name=metadata1',
                    'Date: Dec, 20 Dec 2018 15:00:00 GMT',
                    '',
                    'lvting',
                    '--{b}--'.format(b=self.test_multipart.boundary),
                ]
            ],
            [
                [
                    {
                        'name': 'metadata2',
                        'value': [
                                     open('/tmp/a.txt'),
                                     os.path.getsize('/tmp/a.txt')
                                 ],
                    }
                ],
                [
                    '--{b}'.format(b=self.test_multipart.boundary),
                    'Content-Disposition: form-data; name=metadata2',
                    '',
                    str1,
                    '--{b}--'.format(b=self.test_multipart.boundary),
                ]
            ],
            [
                [
                    {
                        'name': 'metadata3',
                        'value': [file_reader, file_size, 'b.txt'],
                    }
                ],
                [
                    '--{b}'.format(b=self.test_multipart.boundary),
                    'Content-Disposition: form-data; name=metadata3; '
                        + 'filename=b.txt',
                    'Content-Type: text/plain',
                    '',
                    str2,
                    '--{b}--'.format(b=self.test_multipart.boundary),
                ]
            ],
            [
                [
                    {
                        'name': 'metadata4',
                        'value': [str_reader, str_size],
                    }
                ],
                [
                    '--{b}'.format(b=self.test_multipart.boundary),
                    'Content-Disposition: form-data; name=metadata4',
                    '',
                    str3,
                    '--{b}--'.format(b=self.test_multipart.boundary),
                ]
            ],
            [
                [
                    {
                        'name': 'metadata5',
                        'value': ['234ffhhif3323jjfjf3']
                    }
                ],
                [
                    '--{b}'.format(b=self.test_multipart.boundary),
                    'Content-Disposition: form-data; name=metadata5',
                    '',
                    '234ffhhif3323jjfjf3',
                    '--{b}--'.format(b=self.test_multipart.boundary),
                ]
            ],
        ]
        for c in case:
            body = self.test_multipart.make_body_reader(c[0])
            data = []
            for x in body:
                data.append(x)

            self.assertEqual('\r\n'.join(c[1]), ''.join(data))
        fsutil.remove('/tmp/a.txt')
        fsutil.remove('/tmp/b.txt')

    def test_raise_invalid_argument_type_error(self):
        cases = [
            ('metadata1', ('lvting',), {}),
            ('metadata2', ('/tmp/x.txt', 1024), {}),
            ('metadata3', [123423, 1024], {}),
        ]

        for case in cases:
            self.assertRaises(
                httpmultipart.InvalidArgumentTypeError,
                self.test_multipart._standardize_field, *case)
