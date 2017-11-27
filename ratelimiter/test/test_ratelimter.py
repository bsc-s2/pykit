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

        r.set_token_per_second(5)
        self.assertEqual(5, r.token_per_second)

    def test_set_capacity(self):
        r = ratelimiter.RateLimiter(2, 10)
        r.set_capacity(100)
        self.assertEqual(100, r.capacity)

        r.set_capacity(1)
        self.assertEqual(1, r.capacity)
        self.assertAlmostEqual(1, r.get_stored(), places=1)

    def test_consume_and_get_stored(self):
        r = ratelimiter.RateLimiter(1, 0.4)
        r.consume(0.4)
        self.assertAlmostEqual(0, r.get_stored(), places=1)
        time.sleep(0.5)
        self.assertAlmostEqual(0.4, r.get_stored(), places=1)
        r.consume(1)
        self.assertAlmostEqual(-0.6, r.get_stored(), places=1)
        time.sleep(0.01)
        self.assertAlmostEqual(-0.59, r.get_stored(), places=1)

    def test_consume_and_get_stored_token_time(self):
        r = ratelimiter.RateLimiter(10, 100)

        consume_time = time.time() + 1
        r.consume(100, consume_time)
        self.assertAlmostEqual(-80, r.get_stored(consume_time), places=1)
        self.assertEqual(r.get_stored(), r.get_stored(consume_time - 1))

        self.assertAlmostEqual(-70, r.get_stored(consume_time + 1), places=1)
