#!/usr/bin/env python2
# coding: utf-8

import time
import unittest

import cacheable


class TestLRU(unittest.TestCase):

    def assure_lru_list(self, lc):

        size = lc.size
        item_head = lc.head
        item_tail = lc.tail
        for i in xrange(size):
            item_head = item_head['next']
            item_tail = item_tail['pre']

        self.assertTrue(item_head == lc.tail and item_tail == lc.head)

    def cmp_lru_with_expect_orderkeys(self, lc, keys):

        item = lc.head['next']
        lru_keys = []
        while item is not None:
            lru_keys.append(item['key'])
            item = item['next']

        self.assertTrue(keys == lru_keys)

    def test_lru_timeout(self):

        cases = {
            'test_item_timeout': ('k1', 'v1', 5, 'expire'),
            'test_item_old': ('k2', 'v2', 4, 'old'),
            'test_item_new': ('k5', 'v5', 1, 'new'),
        }

        lc = cacheable.LRU(10, 4)
        for case_name, case in cases.items():
            key, val, sleep_time, status = case[0], case[1], case[2], case[3]
            lc[key] = val
            time.sleep(sleep_time)

            try:
                (item, old) = lc[key]
                self.assertEqual(item, val)
                self.assertEqual(status,
                                 ('old' if old else 'new'))

            except KeyError:
                self.assure_lru_list(lc)
                self.assertEqual(status, 'expire')

    def test_lru_getitem(self):

        capacity = 4
        cases = (
            ('test_getitem_capacity-1', {'insert_count': 3,
                                         'exist_keys': [0, 1, 2],
                                         'clean_keys': []}),
            ('test_getitem_capacity', {'insert_count': 4,
                                       'exist_keys': [0, 1, 2, 3],
                                       'clean_keys': []}),
            ('test_getitem_capacity+1', {'insert_count': 5,
                                         'exist_keys': [0, 1, 2, 3, 4],
                                         'clean_keys': []}),
            ('test_getitem_capacity1.5', {'insert_count': 6,
                                          'exist_keys': [0, 1, 2, 3, 4, 5],
                                          'clean_keys': []}),
            ('test_getitem_capacity1.5+1', {'insert_count': 7,
                                            'exist_keys': [3, 4, 5, 6],
                                            'clean_keys': [0, 1, 2]}),
        )

        for case_name, case in cases:
            lc = cacheable.LRU(capacity, 10)
            for i in xrange(case['insert_count']):
                lc[i] = 'val%d' % (i)

            for i in xrange(case['insert_count']):
                try:
                    (item, old) = lc[i]
                    self.assertEqual(item, 'val%d' % (i))
                    self.assertEqual(lc.tail['key'], i)
                    self.assertFalse(old)
                    self.assertTrue(i in case['exist_keys'])

                except KeyError:
                    self.assure_lru_list(lc)
                    self.assertTrue(i in case['clean_keys'])

    def test_lru_setitem(self):

        capacity = 4
        cases = (
            ('test_setitem_capacity-1', {'insert_count': 3,
                                         'expect_order_keys': [0, 1, 2]}),
            ('test_setitem_capacity', {'insert_count': 4,
                                       'expect_order_keys': [0, 1, 2, 3]}),
            ('test_setitem_capacity+1', {'insert_count': 5,
                                         'expect_order_keys': [0, 1, 2, 3, 4]}),
            ('test_setitem_capacity1.5', {'insert_count': 6,
                                          'expect_order_keys': [0, 1, 2, 3, 4, 5]}),
            ('test_setitem_capacity1.5+1', {'insert_count': 7,
                                            'expect_order_keys': [3, 4, 5, 6]}),
        )

        for case_name, case in cases:
            lc = cacheable.LRU(capacity, 10)
            for i in xrange(case['insert_count']):
                lc[i] = 'val%d' % (i)

            self.cmp_lru_with_expect_orderkeys(lc, case['expect_order_keys'])

    def test_lru_capacity(self):

        cases = (
                ('test_capacity_empty',
                 0,
                 {0: 0, 1: 0}),

                ('test_capacity_one',
                 1,
                 {1: 1, 2: 1}),

                ('test_capacity_many',
                 10,
                 {9: 9, 10: 10, 13: 13, 15: 15, 16: 10}),
        )

        for case_name, capacity, case in cases:
            for insert_count, expect_count in case.items():
                c = cacheable.LRU(capacity, 60)
                for i in xrange(insert_count):
                    c[i] = 'val'

                self.assertEqual(c.size, expect_count)


need_cache_data = {'key1': [1], 'key2': [2]}


class ClassMember(object):

    @cacheable.ProcessWiseCache.cache('cache_member_deepcopy', capacity=10240, timeout=5 * 60, deref=True)
    def test_deepcopy(self, param):
        return get_need_cache_data(param)

    @cacheable.ProcessWiseCache.cache('cache_member', capacity=10240, timeout=1, deref=False)
    def test_cache(self):
        return time.time()


@cacheable.ProcessWiseCache.cache('cache', capacity=10240, timeout=1, deref=False)
def test_cache():
    return time.time()


@cacheable.ProcessWiseCache.cache('cache_deepcopy', capacity=10240, timeout=5 * 60, deref=True)
def test_deepcopy(param):
    return get_need_cache_data(param)


def get_need_cache_data(param):

    return need_cache_data.get(param, [])


class TestProcessWiseCache(unittest.TestCase):

    def test_cache(self):

        val = test_cache()
        time.sleep(0.5)
        self.assertEqual(val, test_cache())

        time.sleep(2)
        val_timeout = test_cache()
        self.assertNotEqual(val, val_timeout)

    def test_cache_function_in_class(self):

        mm = ClassMember()
        val_mem = mm.test_cache()
        time.sleep(0.5)
        self.assertEqual(val_mem, mm.test_cache())

        time.sleep(2)
        val_mem_timeout = mm.test_cache()
        self.assertNotEqual(val_mem, val_mem_timeout)

    def test_cache_deepcopy(self):

        val = test_deepcopy('key2')
        val[0] = 101
        self.assertNotEqual(test_deepcopy('key2')[0], 101)

    def test_cache_deepcopy_function_in_class(self):

        mm = ClassMember()
        val_mem = mm.test_deepcopy('key1')
        val_mem[0] = 100
        self.assertNotEqual(mm.test_deepcopy('key1')[0], 100)
