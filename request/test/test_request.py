#!/usr/bin/env python2
# coding: utf-8

import unittest
from pykit.request import Request


class TestRequest(unittest.TestCase):
    def test_create_request(self):

        get_case = {
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

        signed_get = Request(get_case, body='foo')

        self.assertEqual('/?acl&foo=bar', signed_get['uri'])
        self.assertEqual(('AWS4-HMAC-SHA256 Credential=access_key/20180101/us-east-1/s3/aws4_request, '
                          'SignedHeaders=content-length;host;x-amz-content-sha256;x-amz-date, '
                          'Signature=67b7e51a89e7bcb8d292272b940d3e040425c160e690c824d9e8d86616e843ae'),
                         signed_get['headers']['Authorization'])
        self.assertEqual('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                         signed_get['headers']['X-Amz-Content-SHA256'])
        self.assertEqual('20180101T120101Z', signed_get['headers']['X-Amz-Date'])

        post_case = {
            'verb': 'POST',
            'uri': '/',
            'headers': {
                'host': '127.0.0.1',
            },
            'fields': {
                'key': 'test_key',
                'Policy': {
                    'expiration': '2019-01-01T12:00:00.000Z',
                    'conditions': [
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

        signed_post = Request(post_case)

        self.assertEqual('AWS4-HMAC-SHA256', signed_post['fields']['X-Amz-Algorithm'])
        self.assertEqual('20180101T120101Z', signed_post['fields']['X-Amz-Date'])
        self.assertEqual('e78f45490d1e075bc7ea47841a3e084364dc69a3d13d21df3a3cb1f7b8df37ab',
                         signed_post['fields']['X-Amz-Signature'])
        self.assertEqual('access_key/20180101/us-east-1/s3/aws4_request',
                         signed_post['fields']['X-Amz-Credential'])
        self.assertEqual(('eyJjb25kaXRpb25zIjogW1sic3RhcnRzLXdpdGgiLCAiJGtleS'
                          'IsICIiXSwgeyJidWNrZXQiOiAidGVzdC1idWNrZXQifV0sICJl'
                          'eHBpcmF0aW9uIjogIjIwMTktMDEtMDFUMTI6MDA6MDAuMDAwWiJ9'),
                         signed_post['fields']['Policy'])

        put_case = {
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

        signed_put = Request(put_case)

        self.assertEqual('/?acl&foo=haha', signed_put['uri'])
        self.assertEqual(('AWS4-HMAC-SHA256 Credential=access_key/20180930/us-east-1/s3/aws4_request, '
                          'SignedHeaders=content-length;host;x-amz-content-sha256;x-amz-date, '
                          'Signature=9c4e4cbe1b58958e9e026c404b0a54ae107e5a90fd2870f31f6d207216e2c4e8'),
                         signed_put['headers']['Authorization'])
        self.assertEqual('UNSIGNED-PAYLOAD', signed_put['headers']['X-Amz-Content-SHA256'])
        self.assertEqual('20180930T120101Z', signed_put['headers']['X-Amz-Date'])

        no_sign_args_put = {
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

        not_signed_put = Request(no_sign_args_put, body='test request')
        self.assertEqual(12, not_signed_put['headers']['Content-Length'])

        for body in not_signed_put['body']:
            res_body = body

        self.assertEqual('test request', res_body)

    def test_unicode(self):
        unicode_str = '测试'.decode('utf-8')
        unicode_get_case = {
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

        signed_get = Request(unicode_get_case)

        self.assertEqual(unicode_str.encode('utf-8'),
                         signed_get['headers']['X-Amz-Content-SHA256'])
        self.assertIsInstance(signed_get['headers']['Authorization'], str)
        self.assertIsInstance(signed_get['headers']['X-Amz-Date'], str)
