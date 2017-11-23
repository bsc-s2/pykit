#!/usr/bin/env python2
# coding: utf-8

import time
import unittest

from pykit import ratelimiter


class TestRateLimiter(unittest.TestCase):
    def test_set_token_per_second(self):
        r = ratelimiter.RateLimiter(1, 2)

        self.assertEqual(1, r.token_per_second)
        r.set_token_per_second(10)

        self.assertEqual(10, r.token_per_second)

    def test_consume_and_get_stored(self):
        r = ratelimiter.RateLimiter(1, 10)
        r.consume(1)
        self.assertAlmostEqual(0, r.get_stored(), places=1)
        time.sleep(5)
        self.assertAlmostEqual(5, r.get_stored(), places=1)
        r.consume(10)
        self.assertAlmostEqual(-5, r.get_stored(), places=1)
        time.sleep(0.1)
        self.assertAlmostEqual(-4.9, r.get_stored(), places=1)

    def test_future(self):
        r = ratelimiter.RateLimiter(10, 100)

        self.assertEqual(100, r.get_stored(time.time() + 10))
        self.assertEqual(10, r.get_stored(time.time() - 10))
        self.assertAlmostEqual(10, r.get_stored(), places=1)
