#!/usr/bin/env python2.6
# coding: utf-8

import unittest

from pykit import awssign


class TestSigner(unittest.TestCase):

    def test_basic(self):
        signer = awssign.Signer('access_key', 'secret_key')
        fields = {
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
        }

        signer.add_post_auth(fields, request_date='20180101T120101Z')

        self.assertEqual('AWS4-HMAC-SHA256', fields['X-Amz-Algorithm'])
        self.assertEqual('20180101T120101Z', fields['X-Amz-Date'])
        self.assertEqual('19235d229144aa2a1d2b1c3a842c96dfb76bca9b75286c2a0aaae8e29f45c5a7',
                         fields['X-Amz-Signature'])
        self.assertEqual('access_key/20180101/us-east-1/s3/aws4_request',
                         fields['X-Amz-Credential'])
        self.assertEqual('eyJleHBpcmF0aW9uIjogIjIwMTgtMDEtMDFUMTI6MDA6MDAuMDAwWiIsICJjb25kaXRpb24iOiBbWyJzdGFydHMtd2l0aCIsICIka2V5IiwgIiJdLCB7ImJ1Y2tldCI6ICJ0ZXN0LWJ1Y2tldCJ9XX0=',
                         fields['Policy'])
