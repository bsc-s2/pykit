#!/usr/bin/env python2
# coding: utf-8

import unittest

import cacheable


class TestCacheable(unittest.TestCase):

    def __init__(self, *args, **argkv):
        super(TestCacheable, self).__init__(*args, **argkv)
        test_case = {
            'test_key1': 'test_val1',
            'test_key2': 'test_val2',
            'test_key3': 'test_val3',
            'test_key4': 'test_val4',
        }

        self.c = cacheable.LRU(10, 300)
        self.ratio_capacity = self.c.capacity * self.c.ratio
        for k, v in test_case.items():
            self.c[k] = v
            if self.c.size == self.ratio_capacity:
                break

    def test_lru_getitem(self):
        self.c['key_get_item'] = 'val_get_item'
        (item, old) = self.c['key_get_item']
        self.assertEqual(item, 'val_get_item', 'test lru get item')

    def test_lru_capacity(self):
        while self.c.size < self.ratio_capacity:
            self.c['d_key%d' % (self.c.size)] = 'd_val%d' % (self.c.size)

        reserve_count = self.c.capacity
        reserve_keys = []
        item = self.c.tail
        for i in range(reserve_count - 1):
            reserve_keys.append(item['key'])
            item = item['pre']
        self.c['test_key_full'] = 'test_val_full'
        reserve_keys.append('test_key_full')
        succ = True
        for key in reserve_keys:
            if key not in self.c.dict.keys():
                succ = False
                break
        if len(reserve_keys) != len(self.c.dict.keys()):
            succ = False
        self.assertTrue(succ, 'test lru auto del old items')

    def test_lru_setitem(self):
        self.c['test_key100'] = 'test_val100'
        self.assertEqual(self.c.tail['key'],
                         'test_key100', 'test lru setitem to tail')

    def test_lru_next_ptr(self):
        size = self.c.size
        item = self.c.head
        for ii in range(size):
            item = item['next']
        self.assertEqual(self.c.tail, item, 'test lru next ptr')

    def test_lru_prev_ptr(self):
        size = self.c.size
        item = self.c.tail
        for ii in range(size):
            item = item['pre']
        self.assertEqual(self.c.head, item, 'test lru prev ptr')

    def test_lru_item_timeout(self):
        lc = cacheable.LRU(2, -1)
        lc['kk'] = 'vv'
        succ = False
        try:
            lc['kk']
        except KeyError:
            succ = True
        self.assertTrue(succ, 'test lru item timeout')

    def test_processwisecache_wrapper(self):
        val = test_fun('ttt')
        self.assertEqual(val, 'ttt', 'test wise cache wrapper')

    def test_processwisecache_mem_weapper(self):
        val = test_fun_mem_weapper('aaa', 'bbb')
        self.assertEqual(val, 'aaabbb', 'test mem cache wrapper')


@cacheable.ProcessWiseCache.cache('cache_tt_mem', capacity=10240, timeout=5 * 60, deref=False, ismethod=True)
def test_fun_mem_weapper(a, b):
    return a + b


@cacheable.ProcessWiseCache.cache('cache_tt', capacity=10240, timeout=5 * 60, deref=False)
def test_fun(name):
    return name
