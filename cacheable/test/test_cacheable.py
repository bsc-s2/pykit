#!/usr/bin/env python2
# coding: utf-8

import thread
import time
import unittest

from pykit import cacheable


class TestLRU(unittest.TestCase):

    def _assert_lru_list(self, lru):

        size = lru.size
        item_head = lru.head
        item_tail = lru.tail
        for i in range(size):
            item_head = item_head['next']
            item_tail = item_tail['pre']

        self.assertIs(item_head, lru.tail)
        self.assertIs(item_tail, lru.head)

    def _assert_lru_items_order(self, lru, order_keys):

        item = lru.head['next']
        lru_keys = []
        while item is not None:
            lru_keys.append(item['key'])
            item = item['next']

        self.assertEqual(order_keys, lru_keys)

    def test_lru_timeout(self):

        cases = (
            ('k1', 'v1', 3, True),
            ('k2', 'v2', 1, False),
        )

        lru = cacheable.LRU(10, 2)
        for key, val, sleep_time, is_timeout in cases:
            lru[key] = val
            time.sleep(sleep_time)

            try:
                lru[key]
                self.assertFalse(is_timeout)

            except KeyError:
                self._assert_lru_list(lru)
                self.assertTrue(is_timeout)

    def test_lru_getitem(self):

        capacity = 4
        cases = (
            (3,
             [0, 1, 2],
             []),

            (4,
             [0, 1, 2, 3],
             []),

            (5,
             [0, 1, 2, 3, 4],
             []),

            (6,
             [0, 1, 2, 3, 4, 5],
             []),

            (7,
             [3, 4, 5, 6],
             [0, 1, 2]),
        )

        for insert_count, exist_items, cleanup_items in cases:
            lru = cacheable.LRU(capacity, 10)
            for i in range(insert_count):
                lru[i] = 'val%d' % (i)

            for i in range(insert_count):
                try:
                    val = lru[i]
                    self.assertEqual(val, 'val%d' % (i))
                    self.assertEqual(lru.tail['key'], i)
                    self.assertIn(i, exist_items)

                except KeyError:
                    self.assertIn(i, cleanup_items)

    def test_lru_setitem(self):

        capacity = 4
        cases = (
            (3,
             [0, 1, 2]),

            (4,
             [0, 1, 2, 3]),

            (5,
             [0, 1, 2, 3, 4]),

            (6,
             [0, 1, 2, 3, 4, 5]),

            # size of lru > capacity*1.5
            # clean items from head, until size=capacity
            (7,
             [3, 4, 5, 6]),
        )

        for insert_count, expect_order_keys in cases:
            lru = cacheable.LRU(capacity, 10)
            for i in range(insert_count):
                lru[i] = 'val'
                self._assert_lru_list(lru)

            self._assert_lru_items_order(lru, expect_order_keys)

    def test_lru_capacity(self):

        cases = (
                (0,
                 ((0, 0), (1, 0))),

                (1,
                 ((1, 1), (2, 1))),

                (10,
                 ((9, 9), (10, 10), (13, 13), (15, 15), (16, 10))),
        )

        for capacity, case in cases:
            for insert_count, expect_size in case:
                lru = cacheable.LRU(capacity, 60)
                for i in range(insert_count):
                    lru[i] = 'val'

                self.assertEqual(lru.size, expect_size)


class TestCacheable(unittest.TestCase):

    @cacheable.cache('method_cache_data', capacity=10, timeout=4, is_deepcopy=False)
    def _method_cache_data(self, key):
        data = need_cache_data.get(key, {})
        data['tm'] = time.time()
        return data

    def test_get_items_from_cache(self):

        cache_items = {}
        for key in need_cache_data.iterkeys():
            cache_items[key] = get_cache_data(key)

        time.sleep(0.1)
        for key in need_cache_data.iterkeys():
            self.assertEqual(get_cache_data(key), cache_items[key])

    def test_get_items_from_cache_use_method(self):

        cache_items = {}
        for key in need_cache_data.iterkeys():
            cache_items[key] = self._method_cache_data(key)

        time.sleep(0.1)
        for key in need_cache_data.iterkeys():
            self.assertEqual(self._method_cache_data(key), cache_items[key])

    def test_cache_item_timeout_and_cache_again(self):

        cases = (
            (2, False),
            (3, True),
        )

        tm = get_cache_data('key')['tm']
        for sleep_time, is_timeout in cases:
            time.sleep(sleep_time)
            if is_timeout:
                self.assertNotEqual(tm, get_cache_data('key')['tm'])
            else:
                self.assertEqual(tm, get_cache_data('key')['tm'])

    def test_get_deepcopy_item_from_cache(self):

        self.assertIsNot(get_deepcopy_of_cache_data('key1'),
                         get_deepcopy_of_cache_data('key1'))

    def test_get_concurrent_update_cache_data(self):

        result = {}
        def _store_result(key):
            result[key] = get_concurrent_update_cache_data()

        thread.start_new_thread(_store_result, ('key1',))
        time.sleep(1)
        thread.start_new_thread(_store_result, ('key2',))

        while True:
            if 'key2' in result:
                break
            time.sleep(0.1)

        self.assertIsNot(result['key1'], result['key2'])

    def test_get_mutext_update_cache_data(self):

        result = {}
        def _store_result(key):
            result[key] = get_mutex_update_cache_data()

        thread.start_new_thread(_store_result, ('key1',))
        time.sleep(1)
        thread.start_new_thread(_store_result, ('key2',))

        while True:
            if 'key2' in result:
                break
            time.sleep(0.1)

        self.assertIs(result['key1'], result['key2'])

    def test_generate_lru_key(self):

        cases = (
            ((),
             {},
             "[(), []]"),

            ((1),
             {1: 'val_1'},
             "[1, [(1, 'val_1')]]"),

            ((1),
             {'a': 'val_a'},
             "[1, [('a', 'val_a')]]"),

            (('c'),
             {'b': 'val_b'},
             "['c', [('b', 'val_b')]]"),

            ((1, 'c'),
             {'a': 'val_a', 'b': 'val_b'},
             "[(1, 'c'), [('a', 'val_a'), ('b', 'val_b')]]"),

            (('c', 1),
             {'b': 'val_b', 'a': 'val_a'},
             "[('c', 1), [('a', 'val_a'), ('b', 'val_b')]]"),
        )

        for args, argkv, expect_str in cases:
            self.assertEqual(cacheable.Cacheable()._arg_str(args, argkv),
                             expect_str)


@cacheable.cache('deepcopy_of_cache_data', capacity=100, timeout=60, is_deepcopy=True)
def get_deepcopy_of_cache_data(key):

    return need_cache_data.get(key, {})


@cacheable.cache('cache_data', capacity=100, timeout=4, is_deepcopy=False)
def get_cache_data(key):

    cache_data = need_cache_data.get(key, {})
    cache_data['tm'] = time.time()
    return cache_data

@cacheable.cache('concurrent_update_cache_data', capacity=100, timeout=60,
                    is_deepcopy=False, mutex_update=False)
def get_concurrent_update_cache_data():
    time.sleep(3)
    return {}

@cacheable.cache('mutex_update_cache_data', capacity=100, timeout=60,
                    is_deepcopy=False, mutex_update=True)
def get_mutex_update_cache_data():
    time.sleep(3)
    return {}

need_cache_data = {
    'key1': {'tm': 0},
    'key2': {'tm': 0},
    'key3': {'tm': 0},
    'key4': {'tm': 0},
}
