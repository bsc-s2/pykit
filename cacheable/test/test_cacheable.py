#!/usr/bin/env python2
# coding: utf-8

import time
import unittest

from pykit import cacheable


class TestLRU(unittest.TestCase):

    def _assure_lru_list(self, lc):

        size = lc.size
        item_head = lc.head
        item_tail = lc.tail
        for i in xrange(size):
            item_head = item_head['next']
            item_tail = item_tail['pre']

        self.assertTrue(item_head == lc.tail and item_tail == lc.head)

    def _assure_lru_items_order(self, lc, order_keys):

        item = lc.head['next']
        lru_keys = []
        while item is not None:
            lru_keys.append(item['key'])
            item = item['next']

        self.assertTrue(order_keys == lru_keys)

    def test_lru_timeout(self):

        cases = (
            ('k1', 'v1', 5, True, True),
            ('k2', 'v2', 4, True, False),
            ('k3', 'v3', 1, False, False),
        )

        lc = cacheable.LRU(10, 4)
        for key, val, sleep_time, is_old, is_timeout in cases:
            lc[key] = val
            time.sleep(sleep_time)

            try:
                (_, old) = lc[key]
                self.assertEqual(old, is_old)
                self.assertFalse(is_timeout)

            except KeyError:
                self._assure_lru_list(lc)
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
            lc = cacheable.LRU(capacity, 10)
            for i in xrange(insert_count):
                lc[i] = 'val%d' % (i)

            for i in xrange(insert_count):
                try:
                    (item, _) = lc[i]
                    self.assertEqual(item, 'val%d' % (i))
                    self.assertEqual(lc.tail['key'], i)
                    self.assertTrue(i in exist_items)

                except KeyError:
                    self.assertTrue(i in cleanup_items)

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

            (7,
             [3, 4, 5, 6]),
        )

        for insert_count, expect_order_keys in cases:
            lc = cacheable.LRU(capacity, 10)
            for i in xrange(insert_count):
                lc[i] = 'val'
                self._assure_lru_list(lc)

            self._assure_lru_items_order(lc, expect_order_keys)

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
                c = cacheable.LRU(capacity, 60)
                for i in xrange(insert_count):
                    c[i] = 'val'

                self.assertEqual(c.size, expect_size)


class TestProcessWiseCache(unittest.TestCase):

    @cacheable.ProcessWiseCache.cache('method_cache_data', capacity=10, timeout=4, is_deepcopy=False)
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
            (1, False),
            (2, False),
            (2, True),
        )

        tm = get_cache_data('key')['tm']
        for sleep_time, is_timeout in cases:
            time.sleep(sleep_time)
            if is_timeout:
                self.assertNotEqual(tm, get_cache_data('key')['tm'])
            else:
                self.assertEqual(tm, get_cache_data('key')['tm'])

    def test_get_deepcopy_item_from_cache(self):

        data = get_deepcopy_of_cache_data('key1')
        data['tm'] = 10000
        self.assertNotEqual(get_deepcopy_of_cache_data('key1'), data)

    def test_default_key_extractor(self):

        cases = (
            ((),
             {},
             '[(), []]'),

            ((1),
             {1: 'val_1'},
             '[1, [(1, \'val_1\')]]'),

            ((1),
             {'a': 'val_a'},
             '[1, [(\'a\', \'val_a\')]]'),

            (('c'),
             {'b': 'val_b'},
             '[\'c\', [(\'b\', \'val_b\')]]'),

            ((1, 'c'),
             {'a': 'val_a', 'b': 'val_b'},
             '[(1, \'c\'), [(\'a\', \'val_a\'), (\'b\', \'val_b\')]]'),

            (('c', 1),
             {'b': 'val_b', 'a': 'val_a'},
             '[(\'c\', 1), [(\'a\', \'val_a\'), (\'b\', \'val_b\')]]'),
        )

        for args, argkv, expect_str in cases:
            s = cacheable.ProcessWiseCache.arg_str(args, argkv)
            self.assertEqual(s, expect_str)

    def test_define_key_extractor(self):

        cases = (
            ('valueerror',
             cacheable.ProcessWiseCache.arg_str(('valueerror', ), {})),

            ('typeerror',
             cacheable.ProcessWiseCache.arg_str(('typeerror', ), {})),

            ('key',
             key_extractor_funtion(('key', ), {}))
        )

        lru_obj = cacheable.ProcessWiseCache.cachers['cache_data'].c
        for key, expect_generate_key in cases:
            get_cache_data(key)
            self.assertTrue(lru_obj.items.has_key(expect_generate_key))


def key_extractor_funtion(args, argkv):

    if 'valueerror' in args:
        raise ValueError

    if 'typeerror' in args:
        raise TypeError

    return str(args) + str(argkv)


@cacheable.ProcessWiseCache.cache('deepcopy_of_cache_data', capacity=100, timeout=60, is_deepcopy=True)
def get_deepcopy_of_cache_data(key):

    return need_cache_data.get(key, {})


@cacheable.ProcessWiseCache.cache('cache_data', capacity=100, timeout=4,
                                  is_deepcopy=False, key_extractor=key_extractor_funtion)
def get_cache_data(key):

    cache_data = need_cache_data.get(key, {})
    cache_data['tm'] = time.time()
    return cache_data


need_cache_data = {
    'key1': {'tm': 0},
    'key2': {'tm': 0},
    'key3': {'tm': 0},
    'key4': {'tm': 0},
}
