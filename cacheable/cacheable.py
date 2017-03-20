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

        self.lock.acquire()

        self.ratio = 1.5

        self.capacity = capacity
        self.timeout = timeout
        self.advisoryTimeout = int(timeout / 2)
        self.size = 0
        self.dict = {}

        self.tail = {'next': None, 'pre': None}
        self.head = {'next': self.tail, 'pre': None}

        self.tail = self.head

        self.lock.release()

    def __getitem__(self, key):

        ctime = time.time().__int__()

        self.lock.acquire()

        try:
            item = self.dict[key]

            if ctime > item['tm'] + self.timeout:
                self.del_item(item)

                # generate KeyError.
                item = self.dict[key]

            item['pre']['next'] = item['next']

            if item['next'] is not None:
                item['next']['pre'] = item['pre']
            else:
                self.tail = item['pre']

            self._to_tail(item)

            return (item['obj'], (ctime > item['tm'] + self.advisoryTimeout))

        finally:
            self.lock.release()

    def __setitem__(self, key, val):
        self.lock.acquire()

        try:
            if self.dict.has_key(key):

                item = self.dict[key]
                item['obj'] = val

                # refresh time
                item['tm'] = time.time().__int__()

                item['pre']['next'] = item['next']
                if item['next'] is not None:
                    item['next']['pre'] = item['pre']
                else:
                    self.tail = item['pre']

                # self._pr( key, "Set: Before move to tail" )
                self._to_tail(item)
                # self._pr( key, "Set: After move to tail" )

            else:

                self.dict[key] = {'key': key,
                                  'obj': val,
                                  'pre': None,
                                  'next': None,
                                  'tm': time.time().__int__()}

                item = self.dict[key]

                # self._pr( key, "ADD: Before move to tail" )

                self._to_tail(item)

                self.size += 1

                # self._pr( key, "ADD: After move to tail" )

                if self.size > self.capacity * self.ratio:
                    self.cleanup()
        finally:
            self.lock.release()

    def _to_tail(self, item):
        self.lock.acquire()
        try:
            self.tail['next'] = item
            item['pre'] = self.tail
            item['next'] = None

            self.tail = item
        finally:
            self.lock.release()

    def del_item(self, item):
        self.lock.acquire()
        try:
            del self.dict[item['key']]

            item['pre']['next'] = item['next']
            if item['next'] is not None:
                item['next']['pre'] = item['pre']
            else:
                self.tail = item['pre']
            self.size -= 1

        finally:
            self.lock.release()

    def cleanup(self):
        self.lock.acquire()
        try:
            while self.size > self.capacity:

                item = self.head['next']

                self.del_item(item)

            self.head['next']['pre'] = self.head

        finally:
            self.lock.release()


class Cacheable(object):

    cachers = {}

    def __init__(self, capacity=1024 * 4, timeout=60, deref=True, keyExtractor=None):
        self.c = LRU(capacity, timeout)
        self.dereference = deref
        self.keyExtractor = keyExtractor or Cacheable.arg_str
        self.name = '-no-name-'

        self.cacheHit = 0
        self.cacheMissed = 0

    @classmethod
    def cache(clz, name, capacity=1024 * 4, timeout=60, deref=True, ismethod=False, keyExtractor=None):
        c = clz.cachers.get(name,
                            clz(capacity, timeout, deref=deref, keyExtractor=keyExtractor))
        clz.cachers[name] = c
        c.name = name

        if ismethod:
            return c.mem_cache_wrapper
        else:
            return c.cache_wrapper

    @staticmethod
    def arg_str(args, argkv):
        argkv = [(k, v) for [k, v] in argkv.items()]
        argkv.sort()

        return str([args, argkv])


class ProcessWiseCache(Cacheable):

    def mem_cache_wrapper(cself, fun):
        def mem_wrapper(_self, *args, **argkv):
            argStr = None
            try:
                argStr = cself.keyExtractor(args, argkv)
            except Exception as e:
                logger.error(repr(e))
                argStr = Cacheable.arg_str(args, argkv)

            v = None

            try:
                (v, isOld) = cself.c[argStr]
                if isOld:
                    v = fun(_self, *args, **argkv)
                    cself.c[argStr] = v

                cself.cacheHit += 1

            except KeyError as e:
                v = fun(_self, *args, **argkv)
                cself.c[argStr] = v

                cself.cacheMissed += 1

            if cself.dereference:
                return copy.deepcopy(v)
            else:
                return v

        return mem_wrapper

    def cache_wrapper(cself, fun):

        def func_wrapper(*args, **argkv):
            argStr = None
            try:
                argStr = cself.keyExtractor(args, argkv)
            except Exception as e:
                logger.error(repr(e))
                argStr = Cacheable.arg_str(args, argkv)

            v = None
            try:
                (v, isOld) = cself.c[argStr]
                if isOld:
                    v = fun(*args, **argkv)
                    cself.c[argStr] = v
            except KeyError as e:
                v = fun(*args, **argkv)
                cself.c[argStr] = v

            if cself.dereference:
                return copy.deepcopy(v)
            else:
                return v

        return func_wrapper


if __name__ == "__main__":
    import genlog
    genlog.init_root_logger()

    import sys

    # x = LRU( 2 )
    # x[ 'a' ] = 1
    # x[ 'b' ] = 2
    # x[ 'a' ] = 1
    # x[ '1' ] = 1
    # x[ 'a' ] = 1
    # x[ '2' ] = 2
    # x[ 'a' ] = 1
    # x[ '3' ] = 3
    # x[ 'a' ] = 1
    # x[ '4' ] = 4
    # x[ 'a' ] = 1
    # x[ '5' ] = 5
    # x[ 'a' ] = 1
    # x[ '6' ] = 6
    # x[ 'a' ] = 1
    # x[ '7' ] = 7

    # import pprint
    # pprint.pprint(x.head)
    # pprint.pprint(x.tail)
    # pprint.pprint(x.dict)

    # print x[ 'a' ]
    # print x[ 'b' ]

    # ###################################
    # import threading
    # import random

    # lru = LRU( 4, 2 )

    # idx=  0

    # class LRUThread(threading.Thread):
    #     # def __init__( self ):
    #         # super( LRUThread, self ).__init__()

    #     def run(self):

    #         for var in range( 10 ):

    #             try:
    #                 lru[ random.randint(0, 20) ]
    #             except KeyError as e:
    #                 pass

    #             lru[ random.randint( 0, 20 ) ] = True

    #             h = lru.head[ 'next' ]
    #             s = []
    #             while h is not None:
    #                 s.append( "%s" % ( h[ 'key' ] ) )
    #                 h = h[ 'next' ]

    #             print ' '.join( s )

    #         return True

    # for i in range( 20 ):
    #     t = LRUThread()
    #     t.start()
    #     t.join()

    # import sys
    # sys.exit()

    def mm():

        class X(object):
            x = 1

            @ProcessWiseCache.cache('test', 10, 1, True)
            def do_it(self):
                self.x += 1
                print 'added:' + str(self.x)
                return self.x

        xx = X()
        for ii in range(10):
            print xx.do_it()
            time.sleep(0.5)

        time.sleep(2)
        print xx.do_it()

        sys.exit()

    mm()

    # import cProfile

    # # cProfile.run( 'mm()', 'profile.txt' )
    # cProfile.run( 'mm()' )
