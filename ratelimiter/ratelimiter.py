#!/usr/bin/env python2
# coding: utf-8

import time
import threading


class RateLimiter(object):
    def __init__(self, token_per_second, burst_second=1):
        self.token_per_second = token_per_second
        self.burst_second = burst_second
        self.capacity = burst_second * token_per_second
        self.stored = float(token_per_second)
        self.sync_time = time.time()

        self.lock = threading.RLock()

    def consume(self, consumed):
        with self.lock:
            self._resynchronize()
            self.stored = self.stored - consumed

    def _resynchronize(self):
        with self.lock:
            now = time.time()
            duration = now - self.sync_time
            self.sync_time = now

            new_tokens = duration * self.token_per_second
            self.stored = min(self.capacity, self.stored + new_tokens)

    def set_token_per_second(self, token_per_second):
        with self.lock:
            self._resynchronize()
            old_capacity = self.capacity
            self.token_per_second = token_per_second
            self.capacity = token_per_second * self.burst_second
            self.stored = self.stored * self.capacity / old_capacity

    def get_stored(self):
        self._resynchronize()
        return self.stored
