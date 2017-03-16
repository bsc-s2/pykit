#!/usr/bin/env python2
# coding: utf-8

import time
import unittest

from pykit import cacheable


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

    def test_lru_item_old_status_and_timeout(self):

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
                (item, old) = lc[key]
                self.assertEqual(item, val)
                self.assertEqual(old, is_old)
                self.assertFalse(is_timeout)

            except KeyError:
                self.assure_lru_list(lc)
                self.assertTrue(is_timeout)

    def test_lru_getitem(self):

        capacity = 4
        cases = (
            {'insert_count': 3,
             'expect_exist_items': [0, 1, 2],
             'expect_cleanup_items': []},

            {'insert_count': 4,
             'expect_exist_items': [0, 1, 2, 3],
             'expect_cleanup_items': []},

            {'insert_count': 5,
             'expect_exist_items': [0, 1, 2, 3, 4],
             'expect_cleanup_items': []},

            {'insert_count': 6,
             'expect_exist_items': [0, 1, 2, 3, 4, 5],
             'expect_cleanup_items': []},

            {'insert_count': 7,
             'expect_exist_items': [3, 4, 5, 6],
             'expect_cleanup_items': [0, 1, 2]},
        )

        for case in cases:
            lc = cacheable.LRU(capacity, 10)
            for i in xrange(case['insert_count']):
                lc[i] = 'val%d' % (i)

            for i in xrange(case['insert_count']):
                try:
                    (item, old) = lc[i]
                    self.assertEqual(item, 'val%d' % (i))
                    self.assertEqual(lc.tail['key'], i)
                    self.assertFalse(old)
                    self.assertTrue(i in case['expect_exist_items'])

                except KeyError:
                    self.assure_lru_list(lc)
                    self.assertTrue(i in case['expect_cleanup_items'])

    def test_lru_setitem(self):

        capacity = 4
        cases = (
            {'insert_count': 3,
             'expect_order_keys': [0, 1, 2]},

            {'insert_count': 4,
             'expect_order_keys': [0, 1, 2, 3]},

            {'insert_count': 5,
             'expect_order_keys': [0, 1, 2, 3, 4]},

            {'insert_count': 6,
             'expect_order_keys': [0, 1, 2, 3, 4, 5]},

            {'insert_count': 7,
             'expect_order_keys': [3, 4, 5, 6]},
        )

        for case in cases:
            lc = cacheable.LRU(capacity, 10)
            for i in xrange(case['insert_count']):
                lc[i] = 'val'

            self.cmp_lru_with_expect_orderkeys(lc, case['expect_order_keys'])

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

    def test_get_items_from_cache(self):

        mm = ClassMember()
        for key in need_cache_data.iterkeys():
            get_cache_data(key)
            mm.get_cache_data(key)

        time.sleep(0.1)
        now = time.time()
        for key, cache_data in need_cache_data.items():
            self.assertEqual(get_cache_data(key), cache_data)
            self.assertEqual(mm.get_cache_data(key), cache_data)
            self.assertNotEqual(now, get_cache_data(key)['tm'])
            self.assertNotEqual(now, mm.get_cache_data(key)['tm'])

    def test_cache_item_timeout_and_cache_again(self):

        cases = (
            (1, False),
            (2, False),
            (2, True),
        )

        cache_time = get_cache_data('key')['tm']
        for sleep_time, is_timeout in cases:
            time.sleep(sleep_time)
            if is_timeout:
                self.assertNotEqual(cache_time, get_cache_data('key')['tm'])
            else:
                self.assertEqual(cache_time, get_cache_data('key')['tm'])

    def test_get_deepcopy_item_from_cache(self):

        deepcopy_cache_data = get_deepcopy_of_cache_data('key1')
        deepcopy_cache_data['tm'] = 10000
        self.assertNotEqual(get_deepcopy_of_cache_data('key1'),
                            deepcopy_cache_data)

    def test_default_key_extractor(self):

        cases = (
            {'args': (), 'argkv': {},
             'expect_str': '[(), []]'},

            {'args': (1), 'argkv': {1: 'val_1'},
             'expect_str': '[1, [(1, \'val_1\')]]'},

            {'args': (1), 'argkv': {'a': 'val_a'},
             'expect_str': '[1, [(\'a\', \'val_a\')]]'},

            {'args': ('c'), 'argkv': {'b': 'val_b'},
             'expect_str': '[\'c\', [(\'b\', \'val_b\')]]'},

            {'args': (1, 'c'), 'argkv': {'a': 'val_a', 'b': 'val_b'},
             'expect_str': '[(1, \'c\'), [(\'a\', \'val_a\'), (\'b\', \'val_b\')]]'},

            {'args': ('c', 1), 'argkv': {'b': 'val_b', 'a': 'val_a'},
             'expect_str': '[(\'c\', 1), [(\'a\', \'val_a\'), (\'b\', \'val_b\')]]'},
        )

        for case in cases:
            s = cacheable.ProcessWiseCache.arg_str(case['args'], case['argkv'])
            self.assertEqual(s, case['expect_str'])

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

    if len(args) > 0 and args.count('valueerror') > 0:
        raise ValueError

    if len(args) > 0 and args.count('typeerror') > 0:
        raise TypeError

    return str(args) + str(argkv)


class ClassMember(object):

    @cacheable.ProcessWiseCache.cache('member_cache_data', capacity=10, timeout=4, is_deepcopy=False)
    def get_cache_data(self, key):
        cache_data = need_cache_data.get(key, {})
        cache_data['tm'] = time.time()
        return cache_data


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
    'key1': {'data': 'cache_data1', 'tm': 0},
    'key2': {'data': 'cache_data2', 'tm': 0},
    'key3': {'data': 'cache_data3', 'tm': 0},
    'key4': {'data': 'cache_data4', 'tm': 0},
    'key5': {'data': 'cache_data5', 'tm': 0},
    'key6': {'data': 'cache_data6', 'tm': 0},
    'key7': {'data': 'cache_data7', 'tm': 0},
}
