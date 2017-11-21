#!/usr/bin/env python2
# coding: utf-8

import threading
import time


class RateLimiter(object):
    def __init__(self, token_per_second, capacity):
        self.token_per_second = token_per_second
        self.capacity = capacity
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
            self.token_per_second = token_per_second

    def get_stored(self):
        self._resynchronize()
        return self.stored
