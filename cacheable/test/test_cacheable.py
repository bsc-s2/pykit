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

    def test_lru_timeout(self):

        cases = {
            'test_item_timeout': ('k1', 'v1', 5, True),
            'test_item_old': ('k2', 'v2', 4, True),
            'test_item_new': ('k5', 'v5', 1, False),
        }

        lc = cacheable.LRU(10, 4)
        for case_name, case in cases.items():
            key, val, sleep_time, is_old = case[0], case[1], case[2], case[3]
            lc[key] = val
            time.sleep(sleep_time)

            try:
                (item, old) = lc[key]
                self.assertEqual(item, val)
                self.assertEqual(old, is_old)

            except KeyError:
                self.assure_lru_list(lc)
                self.assertFalse(lc.dict.has_key(key))

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
                 ((0, 0), (1, 0))),

                ('test_capacity_one',
                 1,
                 ((1, 1), (2, 1))),

                ('test_capacity_many',
                 10,
                 ((9, 9), (10, 10), (13, 13), (15, 15), (16, 10))),
        )

        for case_name, capacity, case in cases:
            for insert_count, expect_count in case:
                c = cacheable.LRU(capacity, 60)
                for i in xrange(insert_count):
                    c[i] = 'val'

                self.assertEqual(c.size, expect_count)


class TestProcessWiseCache(unittest.TestCase):

    def test_get_items_from_cache(self):

        mm = ClassMember()
        for ip in ip_to_mac_and_hostname_table.iterkeys():
            mm.get_ether_hostname_inmember(ip)
            get_ether_hostname(ip)

        time.sleep(0.1)
        now = time.time()
        for ip, ether_hostname in ip_to_mac_and_hostname_table.items():
            self.assertEqual(get_ether_hostname(ip), ether_hostname)
            self.assertEqual(mm.get_ether_hostname_inmember(ip),
                             ether_hostname)
            self.assertNotEqual(now, get_ether_hostname(ip)['tm'])
            self.assertNotEqual(now, mm.get_ether_hostname_inmember(ip)['tm'])

    def test_cache_item_timeout_and_cache_again(self):

        cases = (
            ('test_item_is_new', 1, True),
            ('test_item_is_old', 2, True),
            ('test_item_is_timeout', 2, False),
        )

        tm = get_ether_hostname('192.168.1.1')['tm']
        for case_name, sleep_time, get_from_cache in cases:
            time.sleep(sleep_time)
            get_tm = get_ether_hostname('192.168.1.1')['tm']
            if get_from_cache:
                self.assertEqual(tm, get_tm)
            else:
                self.assertNotEqual(tm, get_tm)

    def test_get_deepcopy_item_from_cache(self):

        ether_hostname = get_deepcopy_ether_and_hostname('192.168.1.2')
        ether_hostname['tm'] = 10000
        self.assertNotEqual(get_deepcopy_ether_and_hostname('192.168.1.2'),
                            ether_hostname)

    def test_default_key_extractor(self):

        cases = (
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
            ('define_key_extractor_fucntion_raise_valueerror',
             'x.x.x.x',
             cacheable.ProcessWiseCache.arg_str(('x.x.x.x', ), {})),

            ('define_key_extractor_fucntion_raise_typeerror',
             '123456',
             cacheable.ProcessWiseCache.arg_str(('123456', ), {})),

            ('define_key_extractor_success_generate_key',
             '127.0.0.1',
             key_extractor_funtion(('127.0.0.1', ), {}))
        )

        lru_obj = cacheable.ProcessWiseCache.cachers['ip.ether.hostname'].c
        for case_name, ip, generate_key in cases:
            get_ether_hostname(ip)
            self.assertTrue(lru_obj.dict.has_key(generate_key))


def key_extractor_funtion(args, argkv):

    if len(args) > 0 and args.count('x.x.x.x') > 0:
        raise ValueError

    if len(args) > 0 and args.count('123456') > 0:
        raise TypeError

    return str(args) + str(argkv)


class ClassMember(object):

    @cacheable.ProcessWiseCache.cache('member.ip.ether.hostname', capacity=10, timeout=4, deref=False)
    def get_ether_hostname_inmember(self, ip):

        ether_hostname = ip_to_mac_and_hostname_table.get(ip, {})
        ether_hostname['tm'] = time.time()
        return ether_hostname


@cacheable.ProcessWiseCache.cache('ip.ether.hostname.deepcopy', capacity=100, timeout=60, deref=True)
def get_deepcopy_ether_and_hostname(ip):

    return ip_to_mac_and_hostname_table.get(ip, {})


@cacheable.ProcessWiseCache.cache('ip.ether.hostname', capacity=100, timeout=4,
                                  deref=False, key_extractor=key_extractor_funtion)
def get_ether_hostname(ip):

    ether_hostname = ip_to_mac_and_hostname_table.get(ip, {})
    ether_hostname['tm'] = time.time()
    return ether_hostname


ip_to_mac_and_hostname_table = {
    '192.168.1.1': {'ether': 'aa:aa:aa:aa:aa:aa', 'hostname': 'zhao', 'tm': 0},
    '192.168.1.2': {'ether': 'bb:bb:bb:bb:bb:bb', 'hostname': 'qian', 'tm': 0},
    '192.168.1.3': {'ether': 'cc:cc:cc:cc:cc:cc', 'hostname': 'wang', 'tm': 0},
    '192.168.1.4': {'ether': 'dd:dd:dd:dd:dd:dd', 'hostname': 'feng', 'tm': 0},
    '192.168.1.5': {'ether': 'ee:ee:ee:ee:ee:ee', 'hostname': 'tong', 'tm': 0},
    '192.168.1.6': {'ether': 'ff:ff:ff:ff:ff:ff', 'hostname': 'yang', 'tm': 0},
    '192.168.1.7': {'ether': 'gg:gg:gg:gg:gg:gg', 'hostname': 'zhou', 'tm': 0},
    '192.168.1.8': {'ether': 'hh:hh:hh:hh:hh:hh', 'hostname': 'chen', 'tm': 0},
    '192.168.1.9': {'ether': 'ii:ii:ii:ii:ii:ii', 'hostname': 'shen', 'tm': 0},
}
