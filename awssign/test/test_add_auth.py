#!/usr/bin/env python2.6
# coding: utf-8

import unittest

from pykit import awssign


class TestAddAuth(unittest.TestCase):

    def test_basic(self):
        signer = awssign.Signer('access_key', 'secret_key')
        request = {
            'verb': 'GET',
            'uri': '/',
            'args': {
                'foo': 'bar',
                'acl': True,
            },
            'headers': {
                'host': '127.0.0.1',
            },
            'body': 'foo',
        }

        signer.add_auth(request, sign_payload=True,
                        request_date='20180101T120101Z')
        self.assertEqual('/?acl&foo=bar', request['uri'])
        self.assertEqual('AWS4-HMAC-SHA256 Credential=access_key/20180101/us-east-1/s3/aws4_request, SignedHeaders=host;x-amz-content-sha256;x-amz-date, Signature=c0b1d89ddd41df96454d3a5e2c82afdc44aa19bc6593d4fa54bc277756dcc3ef',
                         request['headers']['Authorization'])
        self.assertEqual('2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae',
                         request['headers']['X-Amz-Content-SHA256'])
        self.assertEqual('20180101T120101Z', request['headers']['X-Amz-Date'])

    def test_query_auth(self):
        signer = awssign.Signer('access_key', 'secret_key')
        request = {
            'verb': 'GET',
            'uri': '/',
            'args': {
                'foo': 'bar',
                'acl': True,
            },
            'headers': {
                'host': '127.0.0.1',
            },
            'body': 'foo',
        }

        signer.add_auth(request, sign_payload=True, query_auth=True,
                        request_date='20180101T120101Z')
        self.assertEqual('/?acl&foo=bar&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Expires=60&X-Amz-Credential=access_key%2F20180101%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-SignedHeaders=host&X-Amz-Date=20180101T120101Z&X-Amz-Signature=7aaac5758f74924ef89431dccebebf65a01e9a932b1eb875422c05d7b46efd86',
                         request['uri'])

    def test_unicode(self):
        unicode_str = '测试'.decode('utf-8')
        signer = awssign.Signer(unicode_str, unicode_str, region=unicode_str,
                                service=u's3')
        request = {
            'verb': u'GET',
            'uri': '/' + unicode_str,
            'args': {
                unicode_str: unicode_str,
            },
            'headers': {
                'Host': '127.0.0.1',
                'x-amz-content-sha256': unicode_str,
                unicode_str: unicode_str,
                u'foo': u'bar',
            },
            'body': unicode_str,
        }

        ctx = signer.add_auth(request, headers_not_to_sign=[unicode_str],
                              request_date=u'20190101T120000Z',
                              signing_date=u'20180101',
                              sign_payload=True)

        self.assertEqual(unicode_str.encode('utf-8'),
                         request['headers']['X-Amz-Content-SHA256'])
        self.assertIsInstance(request['headers']['Authorization'], str)
        self.assertIsInstance(request['headers']['X-Amz-Date'], str)
        self.assertEqual('20190101T120000Z', ctx['request_date'])
        self.assertEqual(
            'foo;host;x-amz-content-sha256;x-amz-date', ctx['signed_headers'])
