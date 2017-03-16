#!/usr/bin/env python2
# coding: utf-8

import time
import unittest

import cacheable


class TestLRU(unittest.TestCase):

    def check_lru_ptr(self, lc):

        size = lc.size
        item_head = lc.head
        item_tail = lc.tail
        for i in xrange(size):
            item_head = item_head['next']
            item_tail = item_tail['pre']

        return item_head == lc.tail and item_tail == lc.head

    def cmp_lru_with_expect_orderkeys(self, lc, keys):

        item = lc.head['next']
        lru_keys = []
        while item is not None:
            lru_keys.append(item['key'])
            item = item['next']

        return keys == lru_keys

    def test_lru_timeout(self):

        cases = {
            'test_item_timeout': ('k1', 'v1', 5),
            'test_item_old': ('k2', 'v2', 4),
            'test_item_new': ('k5', 'v5', 1),
        }

        lc = cacheable.LRU(10, 4)
        for case_name, case in cases.items():
            key, val, sleep_time = case[0], case[1], case[2]
            lc[key] = val
            time.sleep(sleep_time)

            try:
                (item, old) = lc[key]
                self.assertEqual(item, val)
                self.assertEqual(
                    case_name, ('test_item_old' if old else 'test_item_new'))

            except KeyError:
                self.assertTrue(self.check_lru_ptr(lc))
                self.assertEqual(case_name, 'test_item_timeout')

    def test_lru_getitem(self):

        capacity = 4
        cases = (
            ('test_getitem_many', {'count': 3,
                                   'exist': (0, 1, 2),
                                   'clean': ()}),
            ('test_getitem_capacity', {'count': 4,
                                       'exist': (0, 1, 2, 3),
                                       'clean': ()}),
            ('test_getitem_middle', {'count': 5,
                                     'exist': (0, 1, 2, 3, 4),
                                     'clean': ()}),
            ('test_getitem_full', {'count': 6,
                                   'exist': (0, 1, 2, 3, 4, 5),
                                   'clean': ()}),
            ('test_getitem_cleanup', {'count': 7,
                                      'exist': (3, 4, 5, 6),
                                      'clean': (0, 1, 2)}),
        )

        for case_name, case in cases:
            lc = cacheable.LRU(capacity, 10)
            insert_count = case['count']
            exist_keys = case['exist']
            clean_keys = case['clean']
            for i in xrange(insert_count):
                lc[i] = 'val%d' % (i)

            for i in xrange(insert_count):
                try:
                    (item, old) = lc[i]
                    self.assertEqual(item, 'val%d' % (i))
                    self.assertEqual(lc.tail['key'], i)
                    self.assertFalse(old)
                    self.assertTrue(i in exist_keys)

                except KeyError:
                    self.assertTrue(self.check_lru_ptr(lc))
                    self.assertTrue(i in clean_keys)

    def test_lru_setitem(self):

        capacity = 4
        cases = (
            ('test_setitem_many', {'insert_count': 3,
                                   'expect_order_keys': [0, 1, 2]}),
            ('test_setitem_capacity', {'insert_count': 4,
                                       'expect_order_keys': [0, 1, 2, 3]}),
            ('test_setitem_middle', {'insert_count': 5,
                                     'expect_order_keys': [0, 1, 2, 3, 4]}),
            ('test_setitem_full', {'insert_count': 6,
                                   'expect_order_keys': [0, 1, 2, 3, 4, 5]}),
            ('test_setitem_cleanup', {'insert_count': 7,
                                      'expect_order_keys': [3, 4, 5, 6]}),
        )

        for case_name, case in cases:
            insert_count = case['insert_count']
            lc = cacheable.LRU(capacity, 10)
            for i in xrange(insert_count):
                lc[i] = 'val%d' % (i)

            expect_order_keys = case['expect_order_keys']
            result = self.cmp_lru_with_expect_orderkeys(lc, expect_order_keys)
            self.assertTrue(result)

    def test_lru_capacity(self):

        cases = (
            ('test_capacity_empty', 0),
            ('test_capacity_one', 1),
            ('test_capacity_many', 10),
        )

        for case_name, capacity in cases:
            c = cacheable.LRU(capacity, 60)
            cleanup_capacity = int(capacity * 1.5)
            for i in xrange(capacity):
                c[i] = 'val'

            self.assertEqual(c.size, capacity)

            j = capacity
            for j in xrange(cleanup_capacity):
                c[j] = 'val'

            self.assertEqual(c.size, cleanup_capacity)

            c['cleanup'] = 'val'

            self.assertEqual(c.size, capacity)


test_cache_dict = {'param1': [1], 'param2': [2], 'param3': [3], 'param4': [4]}


class TestMem(object):

    @cacheable.ProcessWiseCache.cache('cache_mem_deepcopy', capacity=10240, timeout=5 * 60, deref=True)
    def fun_deepcopy(self, param):
        return get_need_cache_data(param)

    @cacheable.ProcessWiseCache.cache('cache_mem', capacity=10240, timeout=1, deref=False)
    def fun(self):
        return time.time()


@cacheable.ProcessWiseCache.cache('cache', capacity=10240, timeout=1, deref=False)
def test_fun():
    return time.time()


@cacheable.ProcessWiseCache.cache('cache_deepcopy', capacity=10240, timeout=5 * 60, deref=True)
def test_fun_deepcopy(param):
    return get_need_cache_data(param)


def get_need_cache_data(param):

    ret = []
    if test_cache_dict.has_key(param):
        ret = test_cache_dict[param]
    return ret


class TestProcessWiseCache(unittest.TestCase):

    def test_cache(self):

        mm = TestMem()
        val_mem = mm.fun()
        val = test_fun()

        time.sleep(0.5)
        self.assertEqual(val_mem, mm.fun())
        self.assertEqual(val, test_fun())

        time.sleep(2)
        val_mem_timeout = mm.fun()
        val_timeout = test_fun()

        self.assertNotEqual(val_mem, val_mem_timeout)
        self.assertNotEqual(val, val_timeout)

    def test_cache_deepcopy(self):

        mm = TestMem()
        val_mem = mm.fun_deepcopy('param1')
        val_mem[0] = 100
        self.assertNotEqual(mm.fun_deepcopy('param1')[0], 100)

        val = test_fun_deepcopy('param2')
        val[0] = 101
        self.assertNotEqual(test_fun_deepcopy('param2')[0], 101)
