#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit.ectypes import needle_source


def _make_referrer(scope, refkey, ver, is_del):
    return needle_source.Referrer(Scope=scope, RefKey=refkey, Ver=ver, IsDel=is_del)


n0 = {
        'NeedleID': '1',
        'Referrers': [
            _make_referrer('3copy', 'key1', 123, 1),
            _make_referrer('3copy', 'key2', 123, 1),
            _make_referrer('3copy', 'key3', 123, 1),
        ],
        'Size': 10,
        'Url': '/',
        'IsDel': 1,
        'Meta': {'meta': 123},
        'SysMeta': {'sysmeta': 123},
        'Level': 0
    }
n1 = {
        'NeedleID': '1',
        'Referrers': [
            _make_referrer('3copy', 'key1', 123, 0),
            _make_referrer('3copy', 'key2', 123, 0),
            _make_referrer('3copy', 'key4', 123, 0),
        ],
        'Size': 10,
        'Url': '/',
        'IsDel': 0,
        'Meta': {'meta': 1234},
        'SysMeta': {'sysmeta': 1234},
        'Level': 1
    }
n2 = {
        'NeedleID': '1',
        'Referrers': [
            _make_referrer('3copy', 'key3', 123, 0),
            _make_referrer('3copy', 'key5', 123, 0),
            _make_referrer('3copy', 'key6', 123, 1),
        ],
        'Size': 10,
        'Url': '/',
        'IsDel': 0,
        'Meta': {'meta': 12345},
        'SysMeta': {'sysmeta': 12345},
        'Level': 2
    }
n3 = {
        'NeedleID': '2',
        'Referrers': [
            _make_referrer('3copy', 'key1', 123, 1),
            _make_referrer('3copy', 'key6', 123, 1),
        ],
        'Size': 10,
        'Url': '/',
        'IsDel': 1,
        'Meta': {'meta': 123456},
        'SysMeta': {'sysmeta': 123456},
        'Level': 3
    }
n4 = {
        'NeedleID': '2',
        'Referrers': [
            _make_referrer('3copy', 'key1', 123, 0),
            _make_referrer('3copy', 'key6', 123, 0),
        ],
        'Size': 10,
        'Url': '/',
        'IsDel': 0,
        'Meta': {'meta': 1234567},

        'SysMeta': {'sysmeta': 1234567},
        'Level': 4
    }
n5 = {
        'NeedleID': '1',
        'Referrers': [
            _make_referrer('3copy', 'key1', 123, 1),
            _make_referrer('3copy', 'key2', 123, 1),
        ],
        'Size': 10,
        'Url': '',
        'IsDel': 1,
        'Meta': {'meta': 123},
        'SysMeta': {},
        'Level': 0
    }
n6 = {
        'NeedleID': '1',
        'Referrers': [
            _make_referrer('3copy', 'key1', 123, 1),
            _make_referrer('3copy', 'key2', 123, 1),
            _make_referrer('3copy', 'key4', 1243, 0)
        ],
        'Size': 10,
        'Url': '',
        'IsDel': 0,
        'Meta': {'meta': 123},
        'SysMeta': {},
        'Level': 0
}
ref1 = needle_source.Referrer(Scope="3copy", RefKey="key1", Ver=123, IsDel=0)
ref2 = needle_source.Referrer(Scope="2copy", RefKey="key1", Ver=123, IsDel=0)
ref3 = needle_source.Referrer(Scope="3copy", RefKey="key2", Ver=123, IsDel=0)
ref4 = needle_source.Referrer(Scope="3copy", RefKey="key1", Ver=124, IsDel=1)
ref5 = needle_source.Referrer(Scope="3copy", RefKey="key1", Ver=123, IsDel=0)
ref6 = needle_source.Referrer(Scope="3copy", RefKey="key1", Ver=1234, IsDel=0)
ref7 = needle_source.Referrer(Scope="3copy", RefKey="key1", Ver=123, IsDel=1)
ref8 = needle_source.Referrer(Scope="2copy", RefKey="key2", Ver=143, IsDel=0)
ref9 = needle_source.Referrer(Scope="2copy", RefKey="key1", Ver=1234, IsDel=0)
ref10 = needle_source.Referrer(Scope="2copy", RefKey="key1", Ver=124, IsDel=0)
ref11 = needle_source.Referrer(Scope="2copy", RefKey="key2", Ver=123, IsDel=0)
ref12 = needle_source.Referrer(Scope="2copy", RefKey="key2", Ver=124, IsDel=1)
ref13 = needle_source.Referrer(Scope="3copy", RefKey="key12", Ver=123, IsDel=0)
ref14 = needle_source.Referrer(Scope="3copy", RefKey="key1", Ver=12, IsDel=1)
ref15 = needle_source.Referrer(Scope="3copy", RefKey="key2", Ver=12, IsDel=0)

ref16 = needle_source.Referrer(Scope="3copy", RefKey="key3", Ver=1123, IsDel=0)
ref17 = needle_source.Referrer(Scope="3copy", RefKey="key3", Ver=1234, IsDel=0)
ref18 = needle_source.Referrer(Scope="3copy", RefKey="key4", Ver=1243, IsDel=1)
ref19 = needle_source.Referrer(Scope="3copy", RefKey="key5", Ver=123, IsDel=0)
ref20 = needle_source.Referrer(Scope="3copy", RefKey="key6", Ver=123, IsDel=1)
ref21 = needle_source.Referrer(Scope="3copy", RefKey="key3", Ver=123, IsDel=1)
ref22 = needle_source.Referrer(Scope="3copy", RefKey="key3", Ver=1234, IsDel=1)
ref23 = needle_source.Referrer(Scope="3copy", RefKey="key5", Ver=12345, IsDel=1)
ref24 = needle_source.Referrer(Scope="3copy", RefKey="key4", Ver=12345, IsDel=1)
list_test = [1, 2, 3, 4, ]


class TestNeedleSource(unittest.TestCase):

    def test_eq(self):
        self.assertFalse(ref1 == ref2)
        self.assertFalse(ref1 == ref3)
        self.assertFalse(ref1 == ref4)
        self.assertTrue(ref1 == ref5)

    def test_ne(self):
        self.assertTrue(ref1 != ref6)
        self.assertTrue(ref6 != ref7)
        self.assertTrue(ref1 != ref8)
        self.assertFalse(ref1 != ref5)

    def test_ge(self):
        self.assertFalse(ref1 >= ref3)
        self.assertFalse(ref1 >= ref6)
        self.assertTrue(ref1 >= ref9)
        self.assertTrue(ref5 >= ref1)

    def test_gt(self):
        self.assertTrue(ref1 > ref2)
        self.assertFalse(ref1 > ref6)
        self.assertFalse(ref10 > ref1)
        self.assertFalse(ref5 > ref1)

    def test_le(self):
        self.assertTrue(ref1 <= ref7)
        self.assertFalse(ref1 <= ref11)
        self.assertFalse(ref1 <= ref12)
        self.assertTrue(ref5 <= ref1)

    def test_ref_lt(self):
        self.assertTrue(ref1 < ref13)
        self.assertFalse(ref1 < ref14)
        self.assertTrue(ref1 < ref15)
        self.assertFalse(ref1 < ref5)

    def test_is_pair(self):
        self.assertFalse(ref1.is_pair(ref6))
        self.assertFalse(ref1.is_pair(ref11))
        self.assertFalse(ref1.is_pair(ref5))
        self.assertTrue(ref1.is_pair(ref7))

    def test_needle_lt(self):
        n0t = needle_source.NeedleSource(n0)
        n1t = needle_source.NeedleSource(n1)
        n2t = needle_source.NeedleSource(n2)
        n3t = needle_source.NeedleSource(n3)
        self.assertFalse(n0t < n1t)
        self.assertFalse(n0t < n2t)
        self.assertFalse(n1t < n2t)
        self.assertTrue(n0t < n3t)
        self.assertTrue(n0t < None)

    def test_needle_id_equal(self):
        n0eq = needle_source.NeedleSource(n0)
        n1eq = needle_source.NeedleSource(n1)
        n2eq = needle_source.NeedleSource(n2)
        n3eq = needle_source.NeedleSource(n3)
        self.assertTrue(n0eq.needle_id_equal(n1eq))
        self.assertTrue(n0eq.needle_id_equal(n2eq))
        self.assertFalse(n0eq.needle_id_equal(n3eq))

    def test_add_referrer(self):
        n0add = needle_source.NeedleSource(n0)
        n1add = needle_source.NeedleSource(n1)
        n4add = needle_source.NeedleSource(n4)
        n4add.reserve_del = False

        n0add.add_referrer(ref16)
        self.assertIs(len(n0add['Referrers']), 4)
        n0add.add_referrer(ref17)
        self.assertIs(len(n0add['Referrers']), 5)
        n0add.add_referrer(ref18)
        self.assertIs(len(n0add['Referrers']), 6)

        n1add.add_referrer(ref23)
        self.assertTrue(n1add['Referrers'][-1] == ref23)
        self.assertRaises(ValueError, n1add.add_referrer, list_test)
        self.assertRaises(ValueError, n1add.add_referrer, ref24)

        n4add.add_referrer(ref20)
        self.assertIs(len(n4add['Referrers']), 1)
        n4add.add_referrer(ref22)
        self.assertIs(len(n4add['Referrers']), 1)
        n4add.add_referrer(ref19)
        self.assertIs(len(n4add['Referrers']), 2)

    def test_merge_referrer(self):
        n012 = {
                'NeedleID': '1',
                'Referrers': [
                    _make_referrer('3copy', 'key1', 123, 1),
                    _make_referrer('3copy', 'key2', 123, 1),
                    _make_referrer('3copy', 'key3', 123, 1),
                    _make_referrer('3copy', 'key4', 123, 0),
                    _make_referrer('3copy', 'key5', 123, 0),
                    _make_referrer('3copy', 'key6', 123, 1),
                ],
                'Size': 10,
                'Url': '/',
                'IsDel': 0,
                'Meta': {'meta': 12345},
                'SysMeta': {'sysmeta': 12345},
                'Level': 0
            }

        n012_del = {
                    'NeedleID': '1',
                    'Referrers': [
                        _make_referrer('3copy', 'key4', 123, 0),
                        _make_referrer('3copy', 'key5', 123, 0),
                    ],
                    'Size': 10,
                    'Url': '/',
                    'IsDel': 0,
                    'Meta': {'meta': 12345},
                    'SysMeta': {'sysmeta': 12345},
                    'Level': 0
                }

        ndl_src0 = needle_source.NeedleSource(n0)
        ndl_src1 = needle_source.NeedleSource(n1)
        ndl_src2 = needle_source.NeedleSource(n2)
        ndl_src012 = needle_source.NeedleSource(n012)
        ndl_src012_del = needle_source.NeedleSource(n012_del)
        ndl_src3 = needle_source.NeedleSource(n3)

        res = needle_source.merge_referrer([])
        self.assertEqual(None, res)

        res = needle_source.merge_referrer([ndl_src0])
        self.assertEqual(ndl_src0, res)

        res = needle_source.merge_referrer([ndl_src0, ndl_src1, ndl_src2])
        self.assertEqual(ndl_src012, res)

        res = needle_source.merge_referrer([ndl_src2, ndl_src0, ndl_src1])
        self.assertEqual(ndl_src012, res)

        ndl_src0.reserve_del = False
        ndl_src1.reserve_del = False
        ndl_src2.reserve_del = False
        ndl_src3.reserve_del = False

        res = needle_source.merge_referrer([ndl_src0])
        self.assertEqual(None, res)

        res = needle_source.merge_referrer([ndl_src0, ndl_src1, ndl_src2])
        self.assertEqual(ndl_src012_del, res)

        res = needle_source.merge_referrer([ndl_src2, ndl_src1, ndl_src0])
        self.assertEqual(ndl_src012_del, res)

        self.assertRaises(needle_source.NeedleIdNotEqual,
                          needle_source.merge_referrer, [ndl_src2, ndl_src3])

    def test_merge_needle_src_iters(self):
        self.maxDiff = None
        expected = [
                {
                    'NeedleID': '1',
                    'Referrers': [
                        _make_referrer('3copy', 'key1', 123, 1),
                        _make_referrer('3copy', 'key2', 123, 1),
                        _make_referrer('3copy', 'key3', 123, 1),
                        _make_referrer('3copy', 'key4', 123, 0),
                        _make_referrer('3copy', 'key5', 123, 0),
                        _make_referrer('3copy', 'key6', 123, 1),
                    ],
                    'Size': 10,
                    'Url': '/',
                    'IsDel': 0,
                    'Meta': {'meta': 12345},
                    'SysMeta': {'sysmeta': 12345},
                    'Level': 0

                },
                {
                    'NeedleID': '2',
                    'Referrers': [
                        _make_referrer('3copy', 'key1', 123, 1),
                        _make_referrer('3copy', 'key6', 123, 1),
                    ],
                    'Size': 10,
                    'Url': '/',
                    'IsDel': 1,
                    'Meta': {'meta': 1234567},
                    'SysMeta': {'sysmeta': 1234567},
                    'Level': 3
                },
             ]
        expected_del = [
                {
                    'NeedleID': '1',
                    'Referrers': [
                        _make_referrer('3copy', 'key4', 123, 0),
                        _make_referrer('3copy', 'key5', 123, 0),
                    ],
                    'Size': 10,
                    'Url': '/',
                    'IsDel': 0,
                    'Meta': {'meta': 12345},
                    'SysMeta': {'sysmeta': 12345},
                    'Level': 0
                },
            ]

        ndls = []
        for n in (n0, n3, n1, n2, n4):
            ndls.append(needle_source.NeedleSource(n))

        res_ndls = []
        self.assertEqual([], res_ndls)

        res_ndls = []
        for ndl in needle_source.merge_needle_source_iters(ndls[1:2]):
            res_ndls.append(ndl)
        self.assertEqual([ndls[1]], res_ndls)

        res_ndls = []
        for ndl in needle_source.merge_needle_source_iters(ndls[:2], ndls[2:4], ndls[4:]):
            res_ndls.append(ndl)
        self.assertEqual(expected, res_ndls)

        for i in range(len(ndls)):
            ndls[i].reserve_del = False

        res_ndls = []
        for ndl in needle_source.merge_needle_source_iters(ndls[1:2]):
            res_ndls.append(ndl)
        self.assertEqual([], res_ndls)

        res_ndls = []
        for ndl in needle_source.merge_needle_source_iters(ndls[:2], ndls[2:]):
            res_ndls.append(ndl)
        self.assertEqual(expected_del, res_ndls)

        res_ndls = []
        for ndl in needle_source.merge_needle_source_iters(ndls[:2], ndls[2:4]):
            res_ndls.append(ndl)
        self.assertEqual(expected_del, res_ndls)

    def test_update_is_del(self):

        n5_is_del = needle_source.NeedleSource(n5)
        n5_is_del.add_referrer(ref16)
        self.assertIs(n5_is_del['IsDel'], 0)

        n6_is_del = needle_source.NeedleSource(n6)
        n6_is_del.add_referrer(ref18)
        self.assertIs(n6_is_del['IsDel'], 1)

        n6_is_del = needle_source.NeedleSource(n6)
        n6_is_del.reserve_del = False
        n6_is_del.add_referrer(ref18)
        self.assertIs(n6_is_del['IsDel'], 1)

    def test_update_meta_sysmeta_level(self):
        ndl_src1 = needle_source.NeedleSource(n1)
        ndl_src2 = needle_source.NeedleSource(n2)
        res = needle_source.merge_referrer([ndl_src1, ndl_src2])
        self.assertEqual(res['Level'], 1)
        self.assertEqual(res['Meta'], {'meta': 12345})
        self.assertEqual(res['SysMeta'], {'sysmeta': 12345})

        ndl_src3 = needle_source.NeedleSource(n3)
        ndl_src4 = needle_source.NeedleSource(n4)
        res = needle_source.merge_referrer([ndl_src3, ndl_src4])
        self.assertEqual(res['Level'], 3)
        self.assertEqual(res['Meta'], {'meta': 1234567})
        self.assertEqual(res['SysMeta'], {'sysmeta': 1234567})
