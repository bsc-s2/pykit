#!/usr/bin/env python2
# coding: utf-8

import time
import unittest

from pykit import ratelimiter


class TestRateLimiter(unittest.TestCase):
    def test_set_token_per_second(self):
        r = ratelimiter.RateLimiter(1, 2)

        self.assertEqual(1, r.token_per_second)
        time.sleep(1)
        r.set_token_per_second(10)

        self.assertEqual(10, r.token_per_second)
        self.assertEqual(20, r.capacity)
        self.assertAlmostEqual(2, r.stored / 10, places=1)

    def test_consume_and_get_stored(self):
        r = ratelimiter.RateLimiter(1, 2)
        r.consume(1)
        self.assertAlmostEqual(0, r.get_stored(), places=1)
        time.sleep(1)
        self.assertAlmostEqual(1, r.get_stored(), places=1)
