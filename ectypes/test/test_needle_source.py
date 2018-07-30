#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit.ectypes import referrer
from pykit.ectypes import needle_source


def _make_referrer(scope, refkey, ver, is_del):
    return referrer.Referrer(Scope=scope,
                             RefKey=refkey, Ver=ver, IsDel=is_del)


n0 = needle_source.NeedleSource({
        'NeedleID': '1',
        'Referrers': [
            _make_referrer('3copy', 'key1', 123, 0),
            _make_referrer('3copy', 'key2', 123, 1),
            _make_referrer('3copy', 'key3', 123, 0),
        ],
        'Size': 10,
        'Url': '/'
    })
n1 = needle_source.NeedleSource({
        'NeedleID': '123',
        'Referrers': [
            _make_referrer('3copy', 'key1', 123, 1),
            _make_referrer('3copy', 'key2', 123, 1),
            _make_referrer('3copy', 'key3', 123, 0),
        ],
        'Size': 10,
        'Url': '/'
    })
n2 = needle_source.NeedleSource({
        'NeedleID': '0',
        'Referrers': [
            _make_referrer('3copy', 'key1', 123, 1),
            _make_referrer('3copy', 'key2', 123, 1),
            _make_referrer('3copy', 'key3', 1234, 1),
        ],
        'Size': 10,
        'Url': '/'
    })
n3 = needle_source.NeedleSource({
        'NeedleID': '1',
        'Referrers': [
            _make_referrer('3copy', 'key1', 123, 1),
            _make_referrer('3copy', 'key2', 123, 1),
            _make_referrer('3copy', 'key3', 123, 1),
        ],
        'Size': 10,
        'Url': '/'
    })
n4 = needle_source.NeedleSource({
        'NeedleID': '1',
        'Referrers': [
            _make_referrer('3copy', 'key1', 123, 1),
            _make_referrer('3copy', 'key3', 123, 0),
            _make_referrer('3copy', 'key6', 123, 0),
        ],
        'Size': 10,
        'Url': '/'
    })
n4.reserve_del = False

ref0 = referrer.Referrer(Scope="3copy", RefKey="key3", Ver=123, IsDel=1)
ref1 = referrer.Referrer(Scope="3copy", RefKey="key3", Ver=1234, IsDel=0)
ref2 = referrer.Referrer(Scope="3copy", RefKey="key4", Ver=1243, IsDel=1)
ref3 = referrer.Referrer(Scope="3copy", RefKey="key5", Ver=123, IsDel=0)
ref4 = referrer.Referrer(Scope="3copy", RefKey="key6", Ver=123, IsDel=1)
ref5 = referrer.Referrer(Scope="3copy", RefKey="key3", Ver=123, IsDel=1)
ref6 = referrer.Referrer(Scope="3copy", RefKey="key3", Ver=1234, IsDel=1)
ref7 = referrer.Referrer(Scope="3copy", RefKey="key3", Ver=12345, IsDel=1)
ref8 = referrer.Referrer(Scope="3copy", RefKey="key1", Ver=12345, IsDel=1)
ref9 = referrer.Referrer(Scope="3copy", RefKey="key1", Ver=123456, IsDel=1)
ref10 = referrer.Referrer(Scope="3copy", RefKey="key1", Ver=1234567, IsDel=0)
list_test = [1, 2, 3, 4, ]


class TestNeedleSource(unittest.TestCase):

    def test_lt(self):
        self.assertTrue(n0.__lt__(n1))
        self.assertTrue(n0 < n1)
        self.assertFalse(n0.__lt__(n2))
        self.assertFalse(n0 < n2)
        self.assertFalse(n0.__lt__(n3))
        self.assertFalse(n0 < n3)
        self.assertFalse(n0.__lt__(n4))
        self.assertFalse(n0 < n4)

    def test_needle_id_equal(self):
        self.assertFalse(n0.needle_id_equal(n1))
        self.assertFalse(n0.needle_id_equal(n2))
        self.assertTrue(n0.needle_id_equal(n3))
        self.assertTrue(n0.needle_id_equal(n4))

    def test_add_referrer(self):
        n0.add_referrer(ref0)
        self.assertIs(len(n0['Referrers']), 3)
        n0.add_referrer(ref1)
        self.assertIs(len(n0['Referrers']), 4)
        n0.add_referrer(ref2)
        self.assertIs(len(n0['Referrers']), 5)
        n0.add_referrer(ref3)
        self.assertIs(len(n0['Referrers']), 6)

        n1.add_referrer(ref7)
        self.assertTrue(n1['Referrers'][-1] == ref7)
        self.assertRaises(ValueError, n1.add_referrer, list_test)

        n4.add_referrer(ref4)
        self.assertIs(len(n4['Referrers']), 2)
        n4.add_referrer(ref6)
        self.assertIs(len(n4['Referrers']), 2)
        n4.add_referrer(ref5)
        self.assertIs(len(n4['Referrers']), 1)
        n4.add_referrer(ref9)
        self.assertIs(len(n4['Referrers']), 1)
        n4.add_referrer(ref10)
        self.assertIs(len(n4['Referrers']), 2)
