#!/usr/bin/env python2
# coding: utf-8

import time
import threading


class RateLimiter(object):
    def __init__(self, token_per_second, max_burst=1):
        self.token_per_second = token_per_second
        self.max_burst = max_burst
        self.capacity = max_burst * token_per_second
        self.stored = float(token_per_second)
        self.sync_time = time.time()

        self.lock = threading.RLock()

    def consume(self, consumed):
        with self.lock:
            self.stored = self.stored - consumed

    def try_acquire(self, request, timeout=0):
        with self.lock:
            self._resync()
            left = self.stored - request
            if left >= 0:
                self.stored = left
                return True
            else:
                next_free_time = -left / self.token_per_second
                if next_free_time > timeout:
                    return False
                else:
                    self.stored = left
        time.sleep(next_free_time)
        return True

    def _resync(self):
        with self.lock:
            now = time.time()
            duration = now - self.sync_time
            self.sync_time = now

            new_tokens = duration * self.token_per_second
            self.stored = min(self.capacity, self.stored + new_tokens)

    def set_token_per_second(self, token_per_second):
        with self.lock:
            self._resync()
            old_capacity = self.capacity
            self.token_per_second = token_per_second
            self.capacity = token_per_second * self.max_burst
            self.stored = self.stored * self.capacity / old_capacity

    def get_stored(self):
        self._resync()
        return self.stored
