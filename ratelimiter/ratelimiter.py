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

    def _sync(self, token_time=None):
        with self.lock:
            if token_time is None:
                new_sync_time = time.time()
                new_tokens = (new_sync_time - self.sync_time) * self.token_per_second
                self.stored = min(self.capacity, self.stored + new_tokens)
                self.sync_time = new_sync_time
                return self.stored
            else:
                if token_time < self.sync_time:
                    token_time = self.sync_time
                new_tokens = (token_time - self.sync_time) * self.token_per_second
                return min(self.capacity, self.stored + new_tokens)

    def set_token_per_second(self, token_per_second):
        with self.lock:
            self._sync()
            self.token_per_second = token_per_second

    def get_stored(self, token_time=None):
        return self._sync(token_time)
