#!/usr/bin/env python2
# coding: utf-8

import time
import unittest

from pykit import ututil
from pykit import ratelimiter


class TestRateLimiter(unittest.TestCase):
    def test_wait_available(self):
        r = ratelimiter.RateLimiter(1, 2)

        # init empty ,wait for available permits
        with ututil.Timer() as t:
            r.wait_available(1)
            self.assertAlmostEqual(1, t.spent(), places=1)

        # wait for free permits
        time.sleep(2)
        with ututil.Timer() as t:
            r.wait_available(2)
            self.assertAlmostEqual(0, t.spent(), places=1)

    def test_set_permits(self):
        r = ratelimiter.RateLimiter(1, 2)
        self.assertEqual(1, r.permits)
        time.sleep(1)
        r.set_permits(10)
        self.assertEqual(10, r.permits)
        self.assertEqual(20, r.capacity)
        self.assertAlmostEqual(1, r.stored / 10, places=1)

    def test_consume_and_get_stored(self):
        r = ratelimiter.RateLimiter(1, 2)
        r.consume(1)
        self.assertAlmostEqual(-1, r.get_stored(), places=1)
        time.sleep(1)
        self.assertAlmostEqual(0, r.get_stored(), places=1)
