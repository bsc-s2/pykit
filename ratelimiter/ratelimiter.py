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
            self._sync()
            self.stored = self.stored - consumed

    def _sync(self):
        with self.lock:
            now = time.time()
            self.stored = self._get_stored_by_time(now)
            self.sync_time = now

    def _get_stored_by_time(self, future):
        if future < self.sync_time:
            future = self.sync_time
        duration = future - self.sync_time
        new_tokens = duration * self.token_per_second
        return min(self.capacity, self.stored + new_tokens)

    def set_token_per_second(self, token_per_second):
        with self.lock:
            self._sync()
            self.token_per_second = token_per_second

    def get_stored(self, future=None):
        if future is not None:
            return self._get_stored_by_time(future)
        self._sync()
        return self.stored
