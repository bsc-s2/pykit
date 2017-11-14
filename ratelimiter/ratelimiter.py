#!/usr/bin/env python2
# coding: utf-8

import threading
import time


class RateLimiter(object):
    def __init__(self, token_per_second, capacity):
        self.token_per_second = token_per_second
        self.capacity = capacity
        self.stored = float(min(token_per_second, capacity))
        self.sync_time = time.time()

        self.lock = threading.RLock()

    def consume(self, consumed, token_time=None):
        with self.lock:
            self._sync(token_time=token_time)
            self.stored = self.stored - consumed

    def _sync(self, token_time=None):
        with self.lock:
            new_sync_time = token_time or time.time()

            if new_sync_time <= self.sync_time:
                return self.stored

            new_tokens = (new_sync_time - self.sync_time) * self.token_per_second
            self.stored = min(self.capacity, self.stored + new_tokens)
            self.sync_time = new_sync_time

            return self.stored

    def set_token_per_second(self, token_per_second):
        self.token_per_second = token_per_second

    def set_capacity(self, capacity):
        with self.lock:
            self._sync()
            self.capacity = capacity
            self.stored = min(self.stored, self.capacity)

    def get_stored(self, token_time=None):
        return self._sync(token_time=token_time)
