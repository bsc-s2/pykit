#!/usr/bin/env python2
# coding:utf-8

import unittest

from pykit import request


class TestRequest(unittest.TestCase):
    def test_add_auth(self):
        dict1 = {
            'verb': 'GET',
            'uri': '/',
            'args': {
                'foo': 'bar',
                'acl': True,
            },
            'headers': {
                'host': '127.0.0.1',
            },
            'fields': {},
            'sign_args': {
                'access_key': 'access_key',
                'secret_key': 'secret_key',
                'request_date': '20180101T120101Z',
                'sign_payload': True,
            }
        }

        request1 = request.Request(dict1, data='foo')

        self.assertEqual('/?acl&foo=bar', request1['uri'])
        self.assertEqual(('AWS4-HMAC-SHA256 Credential=access_key/20180101/us-east-1/s3/aws4_request, '
                          'SignedHeaders=host;x-amz-content-sha256;x-amz-date, '
                          'Signature=c0b1d89ddd41df96454d3a5e2c82afdc44aa19bc6593d4fa54bc277756dcc3ef'),
                         request1['headers']['Authorization'])
        self.assertEqual('2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae',
                         request1['headers']['X-Amz-Content-SHA256'])
        self.assertEqual('20180101T120101Z', request1['headers']['X-Amz-Date'])

        dict2 = {
            'verb': 'POST',
            'uri': '/',
            'args': {},
            'headers': {
                'host': '127.0.0.1',
            },
            'fields': {
                'key': 'test_key',
                'Policy': {
                    'expiration': '2018-01-01T12:00:00.000Z',
                    'condition': [
                        ['starts-with', '$key', ''],
                        {
                            'bucket': 'test-bucket',
                        },
                    ],
                },
            },
            'sign_args': {
                'access_key': 'access_key',
                'secret_key': 'secret_key',
                'request_date': '20180101T120101Z',
            }
        }

        request2 = request.Request(dict2)

        self.assertEqual('AWS4-HMAC-SHA256', request2['fields']['X-Amz-Algorithm'])
        self.assertEqual('20180101T120101Z', request2['fields']['X-Amz-Date'])
        self.assertEqual('19235d229144aa2a1d2b1c3a842c96dfb76bca9b75286c2a0aaae8e29f45c5a7',
                         request2['fields']['X-Amz-Signature'])
        self.assertEqual('access_key/20180101/us-east-1/s3/aws4_request',
                         request2['fields']['X-Amz-Credential'])
        self.assertEqual(('eyJleHBpcmF0aW9uIjogIjIwMTgtMDEtMDFUMTI6MDA6MDAuMD'
                          'AwWiIsICJjb25kaXRpb24iOiBbWyJzdGFydHMtd2l0aCIsICIk'
                          'a2V5IiwgIiJdLCB7ImJ1Y2tldCI6ICJ0ZXN0LWJ1Y2tldCJ9XX0='),
                         request2['fields']['Policy'])

    def test_unicode(self):
        unicode_str = '测试'.decode('utf-8')
        dict3 = {
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
            'fields': {},
            'sign_args': {
                'access_key': unicode_str,
                'secret_key': unicode_str,
                'headers_not_to_sign': [unicode_str],
                'region': unicode_str,
                'request_date': u'20190101T120000Z',
                'service': u's3',
                'signing_date': u'20180101',
                'sign_payload': True,
            }
        }

        request3 = request.Request(dict3, data=unicode_str)

        self.assertEqual(unicode_str.encode('utf-8'),
                         request3['headers']['X-Amz-Content-SHA256'])
        self.assertIsInstance(request3['headers']['Authorization'], str)
        self.assertIsInstance(request3['headers']['X-Amz-Date'], str)
