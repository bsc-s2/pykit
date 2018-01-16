#!/usr/bin/env python2
# coding: utf-8

import copy
import logging
import threading
import time

logger = logging.getLogger(__name__)
_lock_mutex_update = threading.RLock()


class LRU(object):

    def __init__(self, capacity, timeout=60):

        self.lock = threading.RLock()
        self.capacity = capacity
        self.cleanup_threshold = int(capacity * 1.5)
        self.timeout = timeout
        self.size = 0
        self.items = {}
        self.head = {'next': None, 'pre': None}
        self.tail = self.head

    def __getitem__(self, key):

        with self.lock:
            now = int(time.time())
            item = self.items[key]

            if now > item['tm'] + self.timeout:
                self._del_item(item)
                raise KeyError('{k} is timeout'.format(k=key))

            self._move_to_tail(item)

            return item['val']

    def __setitem__(self, key, val):

        with self.lock:
            if key in self.items:
                item = self.items[key]
                item['val'] = val
                item['tm'] = int(time.time())

                self._move_to_tail(item)

            else:
                self.items[key] = {'key': key,
                                   'val': val,
                                   'pre': None,
                                   'next': None,
                                   'tm': int(time.time())}

                self._move_to_tail(self.items[key])

                self.size += 1

                if self.size > self.cleanup_threshold:
                    self._cleanup()

    def _remove_item(self, item):

        item['pre']['next'] = item['next']
        if item['next'] is not None:
            item['next']['pre'] = item['pre']
        else:
            self.tail = item['pre']

    def _move_to_tail(self, item):

        if item['pre'] is not None:
            self._remove_item(item)

        self.tail['next'] = item
        item['pre'] = self.tail
        item['next'] = None
        self.tail = item

    def _del_item(self, item):

        del self.items[item['key']]
        self._remove_item(item)
        self.size -= 1

    def _cleanup(self):

        while self.size > self.capacity:
            item = self.head['next']
            self._del_item(item)


class Cacheable(object):

    def __init__(self, capacity=1024 * 4, timeout=60,
                    is_deepcopy=True, mutex_update=False):

        self.lru = LRU(capacity, timeout)
        self.is_deepcopy = is_deepcopy
        self.mutex_update = mutex_update

    def _arg_str(self, args, argkv):

        argkv = [(k, v) for k, v in argkv.items()]
        argkv.sort()

        return str([args, argkv])

    def _cache_wrapper(self, fun):

        def func_wrapper(*args, **argkv):

            val = None
            generate_key = self._arg_str(args, argkv)

            try:
                val = self.lru[generate_key]
            except KeyError:
                if self.mutex_update:
                    with _lock_mutex_update:
                        try:
                            val = self.lru[generate_key]
                        except KeyError:
                            val = fun(*args, **argkv)
                            self.lru[generate_key] = val
                else:
                    val = fun(*args, **argkv)
                    self.lru[generate_key] = val

            if self.is_deepcopy:
                return copy.deepcopy(val)
            else:
                return val

        return func_wrapper


caches = {}


def cache(name, capacity=1024 * 4, timeout=60, is_deepcopy=True, mutex_update=False):

    c = caches.get(name)
    if c is None:
        c = Cacheable(capacity=capacity, timeout=timeout,
                      is_deepcopy=is_deepcopy, mutex_update=mutex_update)
        caches[name] = c

    return c._cache_wrapper
