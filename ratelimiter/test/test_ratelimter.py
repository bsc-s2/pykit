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
        r = ratelimiter.RateLimiter(1, 4)
        r.consume(1)
        self.assertAlmostEqual(0, r.get_stored(), places=1)
        time.sleep(5)
        self.assertAlmostEqual(4, r.get_stored(), places=1)
        r.consume(10)
        self.assertAlmostEqual(-6, r.get_stored(), places=1)
        time.sleep(0.1)
        self.assertAlmostEqual(-5.9, r.get_stored(), places=1)

    def test_consume_and_get_stored_token_time(self):
        r = ratelimiter.RateLimiter(10, 100)

        consume_time = time.time() + 1
        r.consume(100, consume_time)
        self.assertAlmostEqual(-80, r.get_stored(consume_time), places=1)
        self.assertEqual(r.get_stored(), r.get_stored(consume_time - 1))

        self.assertAlmostEqual(-70, r.get_stored(consume_time + 1), places=1)
