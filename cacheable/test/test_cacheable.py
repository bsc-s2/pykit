#!/usr/bin/env python2
# coding: utf-8

import time
import unittest
import cacheable

lru_capacity = 3
lru_timeout = 4
ref_dict ={1: 'test'}

class TestCacheable(unittest.TestCase):

    test_lru_case = {
        'one item': {'test_key1': 'test_val1'},
        'many item': {'test_key1': 'test_val1', 'test_key2': 'test_val2'},
        'full': {'test_key1': 'test_val1', 'test_key2': 'test_val2', 'test_key3': 'test_val3'},
        'full_ratio': {'test_key1': 'test_val1', 'test_key2': 'test_val2', 'test_key3': 'test_val3',
                       'test_key4': 'test_val4'},
        'clean_up': {'test_key1': 'test_val1', 'test_key2': 'test_val2', 'test_key3': 'test_val3',
                     'test_key4': 'test_val4', 'test_key5': 'test_val5'},
    }

    def cmp_lru_next_ptr(self, lc):
        size = lc.size
        item = lc.head
        for i in range(size):
            item = item['next']

        return lc.tail == item

    def cmp_lru_prev_ptr(self, lc):
        size = lc.size
        item = lc.tail
        for i in range(size):
            item = item['pre']

        return lc.head == item

    def cmp_lru_expect_keys(self, lc, keys):

        item = lc.head['next']
        index = 0
        while item is not None:
            if item['key'] != keys[index]:
                return False
            item = item['next']
            index += 1

        return True

    def test_lru_timeout(self):

        lc = cacheable.LRU(10, lru_timeout)
        for i in range(10):
            lc['test_key%d' % (i)] = 'test_val%d' % (i)
            time.sleep(1.5)

        # old or timeout item
        for i in range(10):
            key = 'test_key%d' % (i)
            val = 'test_val%d' % (i)
            item_time = time.time().__int__() - lc.dict[key]['tm']
            try:
                (item, old) = lc[key]
                if item_time > int(lru_timeout / 2) and item_time <= lru_timeout:
                    self.assertEqual(item, val, 'test case key:%s' % (key))
                    self.assertTrue(old, 'test case key:%s' % (key))
                elif item_time <= int(lru_timeout / 2):
                    self.assertEqual(item, val, 'test case key:%s' % (key))
                    self.assertFalse(old, 'test case key:%s' % (key))
                else:
                    self.assertTrue(False, 'test case key:%s' % (key))
            except KeyError:
                self.assertTrue(self.cmp_lru_next_ptr(lc))
                self.assertTrue(self.cmp_lru_prev_ptr(lc))

                if item_time > lru_timeout:
                    self.assertTrue(True, 'test case key:%s' % (key))
                else:
                    self.assertTrue(False, 'test case key:%s' % (key))

    def test_lru_getitem(self):

        for k, v in self.test_lru_case.items():
            lc = cacheable.LRU(lru_capacity, lru_timeout)
            clean_keys = []
            exist_keys = []
            ratio_capa = int(lru_capacity * lc.ratio)

            for k_item, v_item in v.items():
                lc[k_item] = v_item
                exist_keys.append(k_item)
                if len(exist_keys) > ratio_capa:
                    while len(exist_keys) > lru_capacity:
                        clean_keys.append(exist_keys[0])
                        del exist_keys[0]

            for i in range(len(exist_keys)):
                (item, old) = lc[exist_keys[i]]
                self.assertEqual(item, v[exist_keys[i]], 'test case key:%s' % (k))
                self.assertEqual(lc.tail['key'], exist_keys[i], 'test case key:%s' % (k))
                self.assertFalse(old, 'test case key:%s' % (k))

            for i in range(len(clean_keys)):
                try:
                    lc[clean_keys[i]]
                    self.assertTrue(False, 'test case key:%s' % (k))
                except KeyError:
                    self.assertTrue(True, 'test case key:%s' % (k))


    def test_lru_cleanup(self):
        lc = cacheable.LRU(lru_capacity, lru_timeout)
        for k, v in self.test_lru_case['full_ratio'].iteritems():
            lc[k] = v

        del_count = int(lru_capacity * lc.ratio + 1 - lru_capacity)
        new_first_item = lc.head['next']
        for i in range(del_count):
            new_first_item = new_first_item['next']

        expect_keys = []
        while new_first_item is not None:
            expect_keys.append(new_first_item['key'])
            new_first_item = new_first_item['next']

        lc['test_key_full'] = 'test_val_full'
        expect_keys.append('test_key_full')

        result = self.cmp_lru_expect_keys(lc, expect_keys)

        self.assertTrue(result, 'test lru cleanup when full')

    def test_lru_setitem(self):

        for k, v in self.test_lru_case.items():
            lc = cacheable.LRU(lru_capacity, lru_timeout)
            keys = []

            for k_item, v_item in v.iteritems():
                lc[k_item] = v_item
                keys.append(k_item)
            while len(keys) > lc.size:
                del keys[0]

            self.assertTrue(self.cmp_lru_expect_keys(lc, keys), 'test lru setitem key:%s' % (k))

    def test_lru_ptr(self):

        for k, v in self.test_lru_case.items():
            lc = cacheable.LRU(3, 1)
            for k_item, v_item in v.iteritems():
                lc[k_item] = v_item
            self.assertTrue(self.cmp_lru_next_ptr(lc), 'test case key:%s' % (k))
            self.assertTrue(self.cmp_lru_prev_ptr(lc), 'test case Key:%s' % (k))

    def test_processwisecache_wrapper(self):
        val = test_fun()
        self.assertEqual(val[1], ref_dict[1])

        val[1] = 'test1011'
        val = test_fun()
        self.assertEqual(val[1], 'test1011')

        val_deref = test_fun_deref()
        val_deref[1] = 'test_22'
        val_deref = test_fun_deref()

        self.assertNotEqual(val_deref[1], 'test_22')

    def test_processwisecache_mem_weapper(self):
        mm = TestMem()
        self.addCleanup
        val = mm.test_mem_weapper()
        self.assertEqual(val[1], ref_dict[1])

        val[1] = 'test11'
        val = mm.test_mem_weapper()
        self.assertEqual(val[1], 'test11')

        val_deref = mm.test_mem_weapper_deref()
        val_deref[1] = 'test_test'
        val_deref = mm.test_mem_weapper_deref()

        self.assertNotEqual(val_deref[1], 'test_test')

class TestMem:

    @cacheable.ProcessWiseCache.cache('cache_tt_mem_deref', capacity=10240, timeout=5 * 60, deref=True, ismethod=True)
    def test_mem_weapper_deref(self):
        return ref_dict

    @cacheable.ProcessWiseCache.cache('cache_tt_mem', capacity=10240, timeout=5 * 60, deref=False, ismethod=False)
    def test_mem_weapper(self):
        return ref_dict

@cacheable.ProcessWiseCache.cache('cache_tt', capacity=10240, timeout=5 * 60, deref=False)
def test_fun():
    return ref_dict

@cacheable.ProcessWiseCache.cache('cache_tt_deref', capacity=10240, timeout=5 * 60, deref=True)
def test_fun_deref():
    return ref_dict
