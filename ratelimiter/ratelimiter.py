#!/usr/bin/env python2
# coding: utf-8

import time
import threading


class RateLimiter(object):
    def __init__(self, permits, max_burst=1):
        self.permits = permits
        self.max_burst = max_burst
        self.max_capacity = max_burst * permits
        self.stored = 0.0
        self.sync_time = time.time()

        self.lock = threading.RLock()

    def consume(self, consumed):
        with self.lock:
            self.stored = self.stored - consumed

    def wait_available(self, request):
        with self.lock:
            self._resync()
            self.stored = self.stored - request
            time_to_sleep = -self.stored / self.permits
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

    def _resync(self):
        with self.lock:
            now = time.time()
            duration = now - self.sync_time
            self.sync_time = now

            new_tokens = duration * self.permits
            self.stored = min(self.max_capacity, self.stored + new_tokens)

    def set_permits(self, permits):
        with self.lock:
            self._resync()
            old_max_capacity = self.max_capacity
            self.permits = permits
            self.max_capacity = permits * self.max_burst
            self.stored = self.stored * self.max_capacity / old_max_capacity

    def left(self):
        self._resync()
        return self.stored
