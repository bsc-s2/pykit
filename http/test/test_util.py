#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import http

class TestUtil(unittest.TestCase):

    def test_headers_add_host(self):

        cases = [
            [
                [{}, 'www.123.com'],
                {'Host': 'www.123.com'}
            ],
            [
                [{'Host': 'www.123.com'}, 'www.abc.com'],
                {'Host': 'www.123.com'}
            ],
        ]

        for case, expected in cases:

            self.assertEqual(
                expected, http.headers_add_host(case[0], case[1]))

    def test_requesr_add_host(self):

        cases = [
            [
                [
                    {
                        'verb': 'PUT',
                        'uri': 'test/test',
                        'args': {'foo': 123},
                        'headers': {'Content-Length': 6},
                        'body': '123abc',
                    },
                    'www.123.com'
                ],
                {
                    'verb': 'PUT',
                    'uri': 'test/test',
                    'args': {'foo': 123},
                    'headers': {'Host': 'www.123.com', 'Content-Length': 6},
                    'body': '123abc',
                }
            ],
            [
                [
                    {
                        'verb': 'PUT',
                        'uri': 'test/test',
                        'args': {'foo': 123},
                        'headers': {'Content-Length': 6},
                        'body': '123abc',
                    },
                    'www.123.com'
                ],
                {
                    'verb': 'PUT',
                    'uri': 'test/test',
                    'args': {'foo': 123},
                    'headers': {'Host': 'www.123.com', 'Content-Length': 6},
                    'body': '123abc',
                }
            ],
        ]

        for case, expected in cases:
            self.assertEqual(
                expected, http.request_add_host(case[0], case[1]))
