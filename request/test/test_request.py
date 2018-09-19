#!/usr/bin/env python2
# coding:utf-8

import unittest

from pykit import request


class TestRequest(unittest.TestCase):
    def test_aws_sign(self):
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
            'body': 'foo',
            'fields': {},
            'do_add_auth': True
        }
        request1 = request.Request(dict1)
        request1.aws_sign('access_key', 'secret_key', sign_payload=True, request_date='20180101T120101Z')

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
            'body': '',
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
            'do_add_auth': True
        }
        request2 = request.Request(dict2)
        request2.aws_sign('access_key', 'secret_key', request_date='20180101T120101Z')

        self.assertEqual('AWS4-HMAC-SHA256', request2['fields']['X-Amz-Algorithm'])
        self.assertEqual('20180101T120101Z', request2['fields']['X-Amz-Date'])
        self.assertEqual('19235d229144aa2a1d2b1c3a842c96dfb76bca9b75286c2a0aaae8e29f45c5a7',
                         request2['fields']['X-Amz-Signature'])
        self.assertEqual('access_key/20180101/us-east-1/s3/aws4_request',
                         request2['fields']['X-Amz-Credential'])
        self.assertEqual(('eyJleHBpcmF0aW9uIjogIjIwMTgtMDEtMDFUMTI6MDA6MDAuMDAwWiIsICJjb25kaXRpb24i'
                          'OiBbWyJzdGFydHMtd2l0aCIsICIka2V5IiwgIiJdLCB7ImJ1Y2tldCI6ICJ0ZXN0LWJ1Y2tldCJ9XX0='),
                         request2['fields']['Policy'])
