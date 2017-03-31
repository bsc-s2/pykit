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
                if old:
                    self.assertEqual(status, 'old')
                else:
                    self.assertEqual(status, 'new')

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


def my_key_extractor(args, argkv):
    return 'my_key'


class ClassMember(object):

    @cacheable.ProcessWiseCache.cache('class_member_deepcopy', capacity=10, timeout=60, deref=True)
    def deepcopy_of_cache_data(self, param):
        return need_cache_data_member.get(param, [])

    @cacheable.ProcessWiseCache.cache('class_member_timeout', capacity=10, timeout=4, deref=False)
    def cache_data_timeout(self):
        return time.time()

    @cacheable.ProcessWiseCache.cache('class_member_cache_data', capacity=10, timeout=4, deref=False)
    def cache_data(self, param):
        return need_cache_data_member.get(param, [])


@cacheable.ProcessWiseCache.cache('cache_timeout', capacity=10, timeout=4, deref=False)
def cache_data_timeout():
    return time.time()


@cacheable.ProcessWiseCache.cache('cache_deepcopy', capacity=10, timeout=60, deref=True)
def deepcopy_of_cache_data(param):
    return need_cache_data.get(param, [])


@cacheable.ProcessWiseCache.cache('cache_data', capacity=10, timeout=60, deref=True)
def cache_data(param):
    return need_cache_data.get(param, [])


@cacheable.ProcessWiseCache.cache('key_extractor', capacity=10,
                                  timeout=60, key_extractor=my_key_extractor)
def user_define_key_extractor():
    return need_cache_data.get('key1', [])


need_cache_data = {'key1': [1], 'key2': [2], 'key3': [3]}
need_cache_data_member = {'key4': [4], 'key5': [5], 'key6': [6]}


class TestProcessWiseCache(unittest.TestCase):

    def test_cache_data(self):

        for param in need_cache_data.iterkeys():
            cache_data(param)

        for param, expect_value in need_cache_data.items():
            self.assertEqual(cache_data(param), expect_value)

    def test_cache_data_class_member(self):

        mm = ClassMember()
        for param in need_cache_data_member.iterkeys():
            mm.cache_data(param)

        for param, expect_value in need_cache_data_member.items():
            self.assertEqual(mm.cache_data(param), expect_value)

    def test_cache_timeout(self):

        cases = (
            ('test_item_is_new', 1, True),
            ('test_item_is_old', 2, True),
            ('test_item_is_timeout', 2, False),
        )

        val = cache_data_timeout()
        for case_name, sleep_time, get_from_cache in cases:
            time.sleep(sleep_time)
            get_val = cache_data_timeout()
            if get_from_cache:
                self.assertEqual(val, get_val)
            else:
                self.assertNotEqual(val, get_val)

    def test_cache_timeout_class_member(self):

        cases = (
            ('test_class_member_item_is_new', 1, True),
            ('test_class_member_item_is_old', 2, True),
            ('test_class_member_item_is_timeout', 2, False),
        )

        mm = ClassMember()
        val_mem = mm.cache_data_timeout()
        for case_name, sleep_time, get_from_cache in cases:
            time.sleep(sleep_time)
            get_val = mm.cache_data_timeout()
            if get_from_cache:
                self.assertEqual(val_mem, get_val)
            else:
                self.assertNotEqual(val_mem, get_val)

    def test_cache_deepcopy(self):

        val = deepcopy_of_cache_data('key2')
        val = ['a']
        self.assertNotEqual(val, deepcopy_of_cache_data('key2'))

    def test_cache_deepcopy_class_member(self):

        mm = ClassMember()
        val_mem = mm.deepcopy_of_cache_data('key4')
        val_mem = ['b']
        self.assertNotEqual(mm.deepcopy_of_cache_data('key4'), val_mem)

    def test_default_key_extractor_args(self):
        cases = (
            {'args': (), 'expect_str': '[(), []]'},
            {'args': ('a'), 'expect_str': '[\'a\', []]'},
            {'args': ('a', 'b', 'c'),
             'expect_str': '[(\'a\', \'b\', \'c\'), []]'},
            {'args': (1), 'expect_str': '[1, []]'},
            {'args': (1, 2, 3), 'expect_str': '[(1, 2, 3), []]'},
            {'args': (1, 'a'), 'expect_str': '[(1, \'a\'), []]'},
        )

        for case in cases:
            s = cacheable.Cacheable.arg_str(case['args'], {})
            self.assertEqual(s, case['expect_str'])

    def test_default_key_extractor_argkv(self):

        cases = (
            {'argkv': {'a': 'val_a'},
             'expect_str': '[(), [(\'a\', \'val_a\')]]'},

            {'argkv': {'a': 'val_a', 'b': 'val_b'},
             'expect_str': '[(), [(\'a\', \'val_a\'), (\'b\', \'val_b\')]]'},

            {'argkv': {'b': 'val_b', 'a': 'val_a'},
             'expect_str': '[(), [(\'a\', \'val_a\'), (\'b\', \'val_b\')]]'},

            {'argkv': {1: 'val_1'},
             'expect_str': '[(), [(1, \'val_1\')]]'},

            {'argkv': {1: 'val_1', 2: 'val_2'},
             'expect_str': '[(), [(1, \'val_1\'), (2, \'val_2\')]]'},

            {'argkv': {2: 'val_2', 1: 'val_1'},
             'expect_str': '[(), [(1, \'val_1\'), (2, \'val_2\')]]'},

            {'argkv': {'b': 'val_b', 1: 'val_1'},
             'expect_str': '[(), [(1, \'val_1\'), (\'b\', \'val_b\')]]'},
        )

        for case in cases:
            s = cacheable.Cacheable.arg_str((), case['argkv'])
            self.assertEqual(s, case['expect_str'])

    def test_default_key_extractor_args_and_argkv(self):

        cases = (
            {'args': (1), 'argkv': {1: 'val_1'},
             'expect_str': '[1, [(1, \'val_1\')]]'},

            {'args': (1), 'argkv': {'a': 'val_a'},
             'expect_str': '[1, [(\'a\', \'val_a\')]]'},

            {'args': ('cc'), 'argkv': {'b': 'val_b'},
             'expect_str': '[\'cc\', [(\'b\', \'val_b\')]]'},
        )

        for case in cases:
            s = cacheable.Cacheable.arg_str(case['args'], case['argkv'])
            self.assertEqual(s, case['expect_str'])

    def test_define_key_extractor(self):

        user_define_key_extractor()
        lru_obj = cacheable.Cacheable.cachers['key_extractor'].c
        self.assertTrue(lru_obj.dict.has_key('my_key'))
