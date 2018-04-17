#!/usr/bin/env python2.6
# coding: utf-8

import unittest

from pykit import awssign

EMPTY_PAYLOAD_HASH = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'


class TestSigner(unittest.TestCase):
    access_key = ''
    secret_key = ''
    signer = awssign.Signer(access_key, secret_key)

    def test_uri_encode_args(self):
        args = {
            'foo': True,
            'foo/': ['bar /', '~bar', True, 'bar', True],
            '?': '&=+',
            ' ': ' '
        }
        expect = {
            'foo': True,
            'foo%2F': ['bar%20%2F', '~bar', True, 'bar', True],
            '%3F': '%26%3D%2B',
            '%20': '%20'
        }

        actual = self.signer._uri_encode_args(args)
        self.assertEqual(expect, actual)

    def test_build_canonical_query_string(self):
        test_cases = (
            ({}, '', 'case 1'),
            ({'foo': True}, 'foo=', 'case 2'),
            ({'foo': [True]}, 'foo=', 'case 3'),
            ({'foo': ['']}, 'foo=', 'case 4'),
            ({'foo': [True, 'bar', True]}, 'foo=', 'case 5'),
            ({'foo': ['bar', True], 'bar': ''}, 'bar=&foo=bar', 'case 6'),
            ({'foo': '', 'bar': True}, 'bar=&foo=', 'case 7'),
            ({'bar': [True, 'bar']}, 'bar=', 'case 8'),
            ({'X-Amz-Signature': 'foo', 'bar': 'bar'}, 'bar=bar', 'case 9'),

        )
        for args, expected, des in test_cases:
            actual = self.signer._build_canonical_query_string(args)
            self.assertEqual(expected, actual, des)

    def test_make_sha256(self):
        str = 'foo'
        expected = '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'
        actual = self.signer._make_sha256(str)
        self.assertEqual(expected, actual)

    def test_make_hmac_sha256(self):
        key = 'foo'
        msg = 'bar'
        expected = 'f9320baf0249169e73850cd6156ded0106e2bb6ad8cab01b7bbbebe6d1065317'
        actual = self.signer._make_hmac_sha256(key, msg, True)
        self.assertEqual(expected, actual)

    def test_query_string_to_args(self):
        test_cases = (
            ('', {}),
            ('foo%2F', {'foo/': True}),
            ('foo%2F=', {'foo/': ''}),
            ('+', {' ': True}),
            ('%20=', {' ': ''}),
            ('foo&foo&foo=&foo=bar', {'foo': [True, True, '', 'bar']}),
            ('foo&bar=bar', {'foo': True, 'bar': 'bar'}),
        )
        for qs, expected in test_cases:
            actual = self.signer._query_string_to_args(qs)
            self.assertEqual(expected, actual)

    def test_args_to_query_string(self):
        test_cases = (
            ({}, ''),
            ({'foo/': True}, 'foo%2F'),
            ({' ': ' '}, '%20=%20'),
            ({'?': ['/', ' ', True]}, '%3F=%2F&%3F=%20&%3F'),
            ({'foo': True, 'bar': ''}, 'foo&bar='),
            ({'foo': [True, '', True], 'bar': True}, 'bar&foo&foo=&foo'),
        )
        for args, expected in test_cases:
            actual = self.signer._args_to_query_string(args)
            self.assertEqual(expected, actual)

    def test_get_request_date(self):
        test_cases = (
            (1481026060, '20161206T120740Z'),
            (1481026060.00, '20161206T120740Z'),
            ('20161206T120741Z', '20161206T120741Z'),
        )

        for request_date_in, expected in test_cases:
            actual = self.signer._get_request_date(request_date_in)
            self.assertEqual(expected, actual)

    def test_clean_query_string(self):
        test_cases = (
            ('', ''),
            ('foo', 'foo'),
            ('X-Amz-Date', ''),
            ('X-Amz-Date=', ''),
            ('X-Amz-Date=bar', ''),
            ('foo&X-Amz-Date=bar&bar', 'foo&bar'),
            ('foo=&' +
             'X-Amz-Algorithm=AWS4-HMAC-SHA256&' +
             'X-Amz-Credential=m%2Faws4_request&' +
             'X-Amz-Date=20150830T123600Z&' +
             'X-Amz-Expires=60&' +
             'X-Amz-SignedHeaders=content-type%3Bhost&' +
             'X-Amz-Signature=81d02', 'foo='),
        )
        for qs, expected in test_cases:
            actual = self.signer._clean_query_string(qs)
            self.assertEqual(expected, actual)

    def test_clean_args(self):
        test_cases = (
            ({}, {}),
            ({'foo': 'bar'}, {'foo': 'bar'}),
            ({'foo': ['bar', True]}, {'foo': ['bar', True]}),
            ({'foo': ['bar', True], 'X-Amz-Date': ''}, {'foo': ['bar', True]}),
            ({'foo': ['bar', True], 'X-Amz-Date': True},
             {'foo': ['bar', True]}),
            ({'foo': ['bar', True], 'X-Amz-Date': [True]},
             {'foo': ['bar', True]}),
            ({'foo': ['bar', True],
              'X-Amz-Date': [True],
              'X-Amz-Algorithm': [''],
              'X-Amz-Credential': 'foo',
              'X-Amz-Expires': 80,
              'X-Amz-SignedHeaders': 'foo;bar',
              'X-Amz-Signature': ' '}, {'foo': ['bar', True]}),
        )
        for args, expected in test_cases:
            actual = self.signer._clean_args(args)
            self.assertEqual(expected, actual)

    def test_trimall(self):
        test_cases = (
            ('', ''),
            ('foo', 'foo'),
            ('  foo', 'foo'),
            ('  foo   ', 'foo'),
            ('  f oo   ', 'f oo'),
            ('  f o   o   ', 'f o o'),
            ('  ~!@#$%^&*()_+   ', '~!@#$%^&*()_+'),
            ('  f , oo<>?,./   ', 'f , oo<>?,./'),
            ('  :    ;  ', ': ;'),
        )
        for str, expected in test_cases:
            actual = self.signer._trimall(str)
            self.assertEqual(expected, actual)

    def test_standardize_headers(self):
        test_cases = (
            ({}, [], '', {}),
            ({'foo': 'bar'}, [], 'foo', {'foo': 'bar'}),
            ({'foo': 'bar'}, ['Foo'], '', {'foo': 'bar'}),
            ({'Foo': 'BAR'}, ['foo'], '', {'foo': 'BAR'}),
            ({'Foo  ': 'BAR'}, ['foo'], '', {'foo': 'BAR'}),
            ({'F  oo  ': 'BAR'}, ['F  oo'], '', {'f  oo': 'BAR'}),
            ({'F  oo  ': '  BA  R  '}, [], 'f  oo', {'f  oo': 'BA R'}),
            ({'foo': 'bar', 'bar': '   '}, [],
             'bar;foo', {'foo': 'bar', 'bar': ''}),
        )
        for headers, not_to_sign_headers, expected_signed_headers, expected_stand_headers in test_cases:
            actual_signed_headers, actual_stand_headers = self.signer._standardize_headers(
                headers, not_to_sign_headers)
            self.assertEqual(expected_signed_headers, actual_signed_headers)
            self.assertEqual(expected_stand_headers, actual_stand_headers)

    def test_modify_request_headers(self):
        test_cases = (
            (1,
             {'headers': {}},
             False,
             False,
             '20161206T000000Z',
             'UNSIGNED-PAYLOAD',
             {'X-Amz-Date': '20161206T000000Z',
              'X-Amz-Content-SHA256': 'UNSIGNED-PAYLOAD'}),

            (2,
             {'headers': {'foo': 'bar'}},
             False,
             True,
             '20161206T000000Z',
             EMPTY_PAYLOAD_HASH,
             {'X-Amz-Date': '20161206T000000Z',
              'X-Amz-Content-SHA256': EMPTY_PAYLOAD_HASH,
              'foo': 'bar'}),

            (3,
             {'headers': {},
              'body': 'foo'},
             False,
             True,
             '20161206T000000Z',
             '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae',
             {'X-Amz-Date': '20161206T000000Z',
              'X-Amz-Content-SHA256': '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'}),

            (4,
             {'headers': {'X-Amz-Date': '000000T000000Z'}},
             False,
             True,
             '20161206T000000Z',
             EMPTY_PAYLOAD_HASH,
             {'X-Amz-Date': '20161206T000000Z',
              'X-Amz-Content-SHA256': EMPTY_PAYLOAD_HASH}),

            (5,
             {'headers': {'Date': 'Wed, 07 Dec 2016 05:20:11 GMT'}},
             False,
             True,
             '20161206T000000Z',
             EMPTY_PAYLOAD_HASH,
             {'X-Amz-Date': '20161206T000000Z',
              'Date': 'Wed, 07 Dec 2016 05:20:11 GMT',
              'X-Amz-Content-SHA256': EMPTY_PAYLOAD_HASH}),

            (6,
             {'headers': {'X-Amz-Content-SHA256': 'foo'}},
             False,
             True,
             '20161206T000000Z',
             'foo',
             {'X-Amz-Date': '20161206T000000Z',
              'X-Amz-Content-SHA256': 'foo'}),

            (7,
             {'headers': {'X-Amz-Content-SHA256': 'foo'},
              'body': 'bar'},
             False,
             True,
             '20161206T000000Z',
             'foo',
             {'X-Amz-Date': '20161206T000000Z',
              'X-Amz-Content-SHA256': 'foo'}),

            (8,
             {'headers': {}},
             True,
             True,
             '20161206T000000Z',
             'UNSIGNED-PAYLOAD',
             {}),

            (9,
             {'headers': {'X-Amz-Date': 'foo'}},
             True,
             True,
             '20161206T000000Z',
             'UNSIGNED-PAYLOAD',
             {'X-Amz-Date': '20161206T000000Z'}),

            (10,
             {'headers': {'Date': 'foo'}},
             True,
             True,
             '20161206T000000Z',
             'UNSIGNED-PAYLOAD',
             {'Date': 'foo'}),

            (11,
             {'headers': {'X-Amz-Content-SHA256': 'foo'},
              'body': 'bar'},
             True,
             True,
             '20161206T000000Z',
             'foo',
             {'X-Amz-Content-SHA256': 'foo'}),
        )

        for i, request, presign, sign_payload, request_date, expected_hashed_payload, expected_headers in test_cases:
            actual_hashed_payload = self.signer._modify_request_headers(
                request, presign, sign_payload, request_date)
            self.assertEqual(expected_hashed_payload, actual_hashed_payload,
                             'in case %d: %s, %s' % (i, expected_hashed_payload,
                                                     actual_hashed_payload))
            self.assertEqual(expected_headers, request['headers'],
                             'in case %d: %s, %s' % (i, repr(expected_headers),
                                                     repr(request['headers'])))

    def test_use_both_args_and_query_string(self):
        test_cases = (
            {'verb': 'GET',
             'uri': '/?',
             'args': {},
             'headers': {}, },

            {'verb': 'GET',
             'uri': '/foo/bar?foo',
             'args': {'foo': 'bar'},
             'headers': {}, },

            {'verb': 'GET',
             'uri': '/?',
             'args': {'foo': 'bar'},
             'headers': {}, },
        )
        for request in test_cases:
            with self.assertRaises(Exception):
                self.signer.add_auth(request)

    def test_custom_signing_date(self):
        request = {
            'verb': 'GET',
            'uri': '/',
            'headers': {
                'Host': '127.0.0.1',
            },
        }

        ctx = self.signer.add_auth(request, signing_date='20150102')
        self.assertEqual('20150102/us-east-1/s3/aws4_request',
                         ctx['credential_scope'])
