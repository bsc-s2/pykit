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
        self.dict = {}
        self.head = {'next': None, 'pre': None}
        self.tail = self.head

    def __getitem__(self, key):

        ctime = int(time.time())

        with self.lock:
            item = self.dict[key]

            if ctime > item['tm'] + self.timeout:
                self.del_item(item)
                raise KeyError

            self.move_to_tail(item)

            return (item['obj'], (ctime > item['tm'] + self.item_old_time))

    def __setitem__(self, key, val):

        with self.lock:
            if self.dict.has_key(key):
                item = self.dict[key]
                item['obj'] = val
                item['tm'] = int(time.time())

                self.move_to_tail(item)

            else:
                self.dict[key] = {'key': key,
                                  'obj': val,
                                  'pre': None,
                                  'next': None,
                                  'tm': int(time.time())}

                self.move_to_tail(self.dict[key])

                self.size += 1

                if self.size > self.cleanup_threshold:
                    self.cleanup()

    def _remove_item(self, item):

        item['pre']['next'] = item['next']
        if item['next'] is not None:
            item['next']['pre'] = item['pre']
        else:
            self.tail = item['pre']

    def move_to_tail(self, item):

        with self.lock:
            if item['pre'] is not None:
                self._remove_item(item)

            self.tail['next'] = item
            item['pre'] = self.tail
            item['next'] = None
            self.tail = item

    def del_item(self, item):

        with self.lock:
            del self.dict[item['key']]
            self._remove_item(item)
            self.size -= 1

    def cleanup(self):

        with self.lock:
            while self.size > self.capacity:
                item = self.head['next']
                self.del_item(item)


class Cacheable(object):

    cachers = {}

    def __init__(self, capacity=1024 * 4, timeout=60, deref=True, key_extractor=None):

        self.c = LRU(capacity, timeout)
        self.dereference = deref
        self.key_extractor = key_extractor or Cacheable.arg_str
        self.name = '-no-name-'
        self.cache_hit = 0
        self.cache_missed = 0

    @classmethod
    def cache(clz, name, capacity=1024 * 4, timeout=60, deref=True, key_extractor=None):

        c = clz.cachers.get(name, clz(capacity, timeout,
                                      deref=deref, key_extractor=key_extractor))
        clz.cachers[name] = c
        c.name = name

        return c.cache_wrapper

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
            except (TypeError, ValueError) as e:
                arg_str = Cacheable.arg_str(args, argkv)
                logger.info(repr(e) + ' while generate LRU item key')
            except Exception as e:
                logger.exception(repr(e) + ' while generate LRU item key')

            v = None

            try:
                (v, is_old) = cself.c[arg_str]
                cself.cache_hit += 1
            except KeyError as e:
                v = fun(*args, **argkv)
                cself.c[arg_str] = v
                cself.cache_missed += 1

                logger.info(repr(e)
                            + ' while getitem from LRU, the  key: {s}'.format(s=arg_str))
            except Exception as e:
                logger.exception(repr(e)
                                 + ' while getitem from LRU, the key: {s}'.format(s=arg_str))

            if cself.dereference:
                return copy.deepcopy(v)
            else:
                return v

        return func_wrapper
