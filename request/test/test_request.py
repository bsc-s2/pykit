#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import request


class TestRequest(unittest.TestCase):
    def test_create_request(self):

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
                          'SignedHeaders=content-length;host;x-amz-content-sha256;x-amz-date, '
                          'Signature=67b7e51a89e7bcb8d292272b940d3e040425c160e690c824d9e8d86616e843ae'),
                         request1['headers']['Authorization'])
        self.assertEqual('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                         request1['headers']['X-Amz-Content-SHA256'])
        self.assertEqual('20180101T120101Z', request1['headers']['X-Amz-Date'])

        dict2 = {
            'verb': 'POST',
            'uri': '/',
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

        dict3 = {
            'verb': 'PUT',
            'uri': '/',
            'args': {
                'foo': 'haha',
                'acl': True,
            },
            'headers': {
                'host': '127.0.0.1',
            },
            'sign_args': {
                'access_key': 'access_key',
                'secret_key': 'secret_key',
                'request_date': '20180930T120101Z',
                'sign_payload': False,
            }
        }

        request3 = request.Request(dict3)

        self.assertEqual('/?acl&foo=haha', request3['uri'])
        self.assertEqual(('AWS4-HMAC-SHA256 Credential=access_key/20180930/us-east-1/s3/aws4_request, '
                          'SignedHeaders=content-length;host;x-amz-content-sha256;x-amz-date, '
                          'Signature=9c4e4cbe1b58958e9e026c404b0a54ae107e5a90fd2870f31f6d207216e2c4e8'),
                         request3['headers']['Authorization'])
        self.assertEqual('UNSIGNED-PAYLOAD', request3['headers']['X-Amz-Content-SHA256'])
        self.assertEqual('20180930T120101Z', request3['headers']['X-Amz-Date'])

        dict4 = {
            'verb': 'PUT',
            'uri': '/',
            'args': {
                'foo': 'bar',
                'acl': True,
            },
            'headers': {
                'host': '127.0.0.1',
            },
        }

        request4 = request.Request(dict4, data='test request')
        self.assertEqual(12, request4['headers']['Content-Length'])

        for body in request4['body']:
            res_body = body

        self.assertEqual('test request', res_body)

    def test_unicode(self):
        unicode_str = '测试'.decode('utf-8')
        dict5 = {
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

        request3 = request.Request(dict5)

        self.assertEqual(unicode_str.encode('utf-8'),
                         request3['headers']['X-Amz-Content-SHA256'])
        self.assertIsInstance(request3['headers']['Authorization'], str)
        self.assertIsInstance(request3['headers']['X-Amz-Date'], str)
