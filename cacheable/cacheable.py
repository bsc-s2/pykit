#!/usr/bin/env python2
# coding: utf-8

import copy
import logging
import threading
import time

logger = logging.getLogger(__name__)


class LRU(object):

    def __init__(self, capacity, timeout=60):

        self.lock = threading.RLock()
        self.capacity = capacity
        self.cleanup_threshold = int(capacity * 1.5)
        self.timeout = timeout
        self.item_old_time = int(timeout / 2)
        self.size = 0
        self.items = {}
        self.head = {'next': None, 'pre': None}
        self.tail = self.head

    def __getitem__(self, key):

        now = int(time.time())

        with self.lock:
            item = self.items[key]

            if now > item['tm'] + self.timeout:
                self._del_item(item)
                raise KeyError('{k} is timeout'.format(k=key))

            self._move_to_tail(item)

            return (item['val'], (now > item['tm'] + self.item_old_time))

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

        with self.lock:
            if item['pre'] is not None:
                self._remove_item(item)

            self.tail['next'] = item
            item['pre'] = self.tail
            item['next'] = None
            self.tail = item

    def _del_item(self, item):

        with self.lock:
            del self.items[item['key']]
            self._remove_item(item)
            self.size -= 1

    def _cleanup(self):

        with self.lock:
            while self.size > self.capacity:
                item = self.head['next']
                self._del_item(item)


class Cacheable(object):

    cachers = {}

    def __init__(self, capacity=1024 * 4, timeout=60, is_deepcopy=True, key_extractor=None):

        self.lru = LRU(capacity, timeout)
        self.is_deepcopy = is_deepcopy
        self.key_extractor = key_extractor or Cacheable.arg_str
        self.name = '-no-name-'
        self.cache_hit = 0
        self.cache_missed = 0

    @classmethod
    def cache(clz, name, capacity=1024 * 4, timeout=60, is_deepcopy=True, key_extractor=None):

        cacher = clz.cachers.get(name, clz(capacity, timeout,
                                           is_deepcopy, key_extractor))
        clz.cachers[name] = cacher
        cacher.name = name

        return cacher.cache_wrapper

    @staticmethod
    def arg_str(args, argkv):

        argkv = [(k, v) for [k, v] in argkv.items()]
        argkv.sort()

        return str([args, argkv])


class ProcessWiseCache(Cacheable):

    def cache_wrapper(cself, fun):

        def func_wrapper(*args, **argkv):

            arg_str = None

            try:
                arg_str = cself.key_extractor(args, argkv)
            except Exception as e:
                arg_str = Cacheable.arg_str(args, argkv)
                logger.exception(repr(e) + ' while generate LRU item key')

            val = None

            try:
                (val, is_old) = cself.lru[arg_str]
                cself.cache_hit += 1
            except KeyError as e:
                val = fun(*args, **argkv)
                cself.lru[arg_str] = val
                cself.cache_missed += 1

                logger.info(repr(e)
                            + ' while getitem from LRU, the  key: {s}'.format(s=arg_str))

            if cself.is_deepcopy:
                return copy.deepcopy(val)
            else:
                return val

        return func_wrapper
