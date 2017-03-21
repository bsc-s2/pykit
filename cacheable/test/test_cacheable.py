#!/usr/bin/env python2
# coding: utf-8

import time
import unittest
import cacheable

LRU_CAPACITY = 3
LRU_TIMEOUT = 4

class TestLRU(unittest.TestCase):

    test_lru_case = {
        'one item': {'key1': 'val1'},
        'many item': {'key1': 'val1', 'key2': 'val2'},
        'full': {'key1': 'val1', 'key2': 'val2', 'key3': 'val3'},
        'full_ratio': {'key1': 'val1', 'key2': 'val2', 'key3': 'val3',
                       'key4': 'val4'},
        'clean_up': {'key1': 'val1', 'key2': 'val2', 'key3': 'val3',
                     'key4': 'val4', 'key5': 'val5'},
    }

    def check_lru_ptr(self, lc):
        size = lc.size
        item_head = lc.head
        item_tail = lc.tail
        for i in xrange(size):
            item_head = item_head['next']
            item_tail = item_tail['pre']

        return item_head == lc.tail and item_tail == lc.head

    def cmp_lru_with_expect_keys(self, lc, keys):

        item = lc.head['next']
        index = 0
        while item is not None:
            if item['key'] != keys[index]:
                return False
            item = item['next']
            index += 1

        return True

    def test_lru_timeout(self):

        lc = cacheable.LRU(10, LRU_TIMEOUT)
        for i in xrange(10):
            lc['test_key%d' % (i)] = 'test_val%d' % (i)
            time.sleep(1.5)

        # old or timeout item
        for i in xrange(10):
            key = 'test_key%d' % (i)
            val = 'test_val%d' % (i)
            item_time = time.time().__int__() - lc.dict[key]['tm']
            try:
                (item, old) = lc[key]
                if item_time > int(LRU_TIMEOUT / 2) and item_time <= LRU_TIMEOUT:
                    self.assertEqual(item, val, 'test case key:%s' % (key))
                    self.assertTrue(old, 'test case key:%s' % (key))
                elif item_time <= int(LRU_TIMEOUT / 2):
                    self.assertEqual(item, val, 'test case key:%s' % (key))
                    self.assertFalse(old, 'test case key:%s' % (key))
                else:
                    self.assertTrue(False, 'test case key:%s' % (key))
            except KeyError:
                self.assertTrue(self.check_lru_ptr(lc))

                if item_time > LRU_TIMEOUT:
                    self.assertTrue(True, 'test case key:%s' % (key))
                else:
                    self.assertTrue(False, 'test case key:%s' % (key))

    def test_lru_getitem(self):

        for k, v in self.test_lru_case.items():
            lc = cacheable.LRU(LRU_CAPACITY, LRU_TIMEOUT)
            clean_keys = []
            exist_keys = []
            ratio_capacity = int(LRU_CAPACITY * lc.ratio)
            del_count = ratio_capacity + 1 - lc.capacity

            for k_item, v_item in v.items():
                lc[k_item] = v_item
                exist_keys.append(k_item)
                if len(exist_keys) > ratio_capacity:
                    clean_keys += exist_keys[:del_count]
                    exist_keys = exist_keys[del_count:]

            for key in exist_keys:
                (item, old) = lc[key]
                self.assertEqual(item, v[key], 'test case key:%s' % (k))
                self.assertEqual(lc.tail['key'], key, 'test case key:%s' % (k))
                self.assertFalse(old, 'test case key:%s' % (k))

            for key in clean_keys:
                try:
                    lc[key]
                    self.assertTrue(False, 'test case key:%s' % (k))
                except KeyError:
                    self.assertTrue(True, 'test case key:%s' % (k))


    def test_lru_cleanup(self):
        lc = cacheable.LRU(LRU_CAPACITY, LRU_TIMEOUT)
        for k, v in self.test_lru_case['full_ratio'].items():
            lc[k] = v

        del_count = int(LRU_CAPACITY * lc.ratio + 1 - LRU_CAPACITY)
        item = lc.head['next']
        index = 0
        expect_keys = []

        while item is not None:
            if index >= del_count:
               expect_keys.append(item['key'])

            index += 1
            item = item['next']

        lc['test_key_full'] = 'test_val_full'
        expect_keys.append('test_key_full')

        result = self.cmp_lru_with_expect_keys(lc, expect_keys)

        self.assertTrue(result, 'test lru cleanup when full')

    def test_lru_setitem(self):

        for k, v in self.test_lru_case.items():
            lc = cacheable.LRU(LRU_CAPACITY, LRU_TIMEOUT)
            ratio_capacity = int(LRU_CAPACITY * lc.ratio)
            del_count = ratio_capacity + 1 - lc.capacity
            keys = []

            for k_item, v_item in v.iteritems():
                lc[k_item] = v_item
                keys.append(k_item)
                if len(keys) > ratio_capacity:
                    keys = keys[del_count:]

            result = self.cmp_lru_with_expect_keys(lc,keys)
            self.assertTrue(result, 'test lru setitem key:%s' % (k))

    def test_lru_ptr(self):

        for k, v in self.test_lru_case.items():
            lc = cacheable.LRU(LRU_CAPACITY, LRU_TIMEOUT)
            for k_item, v_item in v.iteritems():
                lc[k_item] = v_item
                self.assertTrue(self.check_lru_ptr(lc), 'test case key:%s' % (k))

class TestMem(object):

    @cacheable.ProcessWiseCache.cache('cache_tt_mem_deref', capacity=10240, timeout=5 * 60, deref=True, ismethod=True)
    def test_mem_weapper_deref(self):
        return test_dict

    @cacheable.ProcessWiseCache.cache('cache_tt_mem', capacity=10240, timeout=5 * 60, deref=False, ismethod=False)
    def test_mem_weapper(self):
        return test_dict

@cacheable.ProcessWiseCache.cache('cache_tt', capacity=10240, timeout=5 * 60, deref=False)
def test_fun():
    return test_dict

@cacheable.ProcessWiseCache.cache('cache_tt_deref', capacity=10240, timeout=5 * 60, deref=True)
def test_fun_deref():
    return test_dict

test_dict ={'key': 'val'}
class TestProcessWiseCache(unittest.TestCase):

    def test_processwisecache_wrapper(self):
        val = test_fun()
        self.assertEqual(val['key'], test_dict['key'])

        val['key'] = 'val1'
        val = test_fun()
        self.assertEqual(val['key'], 'val1')

        val_deref = test_fun_deref()
        self.assertEqual(val_deref['key'], test_dict['key'])

        val_deref['key'] = 'val2'
        val_deref = test_fun_deref()
        self.assertNotEqual(val_deref['key'], 'val2')

    def test_processwisecache_mem_weapper(self):
        mm = TestMem()
        val = mm.test_mem_weapper()
        self.assertEqual(val['key'], test_dict['key'])

        val['key'] = 'val3'
        val = mm.test_mem_weapper()
        self.assertEqual(val['key'], 'val3')

        val_deref = mm.test_mem_weapper_deref()
        self.assertEqual(val_deref['key'], test_dict['key'])

        val_deref['key'] = 'val4'
        val_deref = mm.test_mem_weapper_deref()
        self.assertNotEqual(val_deref['key'], 'val4')
