#!/usr/bin/env python2
# coding: utf-8

import copy
import unittest

import imports2
import needle_source

sec_10_ns = 10*1000**3

_phy = {
    "size": 67108864,
    "sha1": "000000198873a5a7ce0581a7ecf67829a54565fe",
    "ver": 1501810996336000101,
    "phy_ts": 1501811013203000101,
    "is_del": 0,
    "ts": 1501811013203000101,
    "bucket_id": 1570000000000000062,
    "key": "0f01510a0d0a46000a01682dfd58aed2/12",
    "crc32": "00000000",
    "scope": "p",
    "origo": "a0369fd807c2",
    "group_id": 665227,
    "md5": "375f49011e6296d038d15a36e266f38b"
}
_case_1 = [_phy]


# deleted phy
_phy = {
    "size": 67108864,
    "sha1": "0000005730b5c60dc45bbb7028d61ef57770fac0",
    "ver": 1506487974847000101,
    "phy_ts": 1506488267429000101,
    "is_del": 0,
    "ts": 1506488267429000101,
    "bucket_id": 1570000000000000062,
    "key": "0f06305243253c000a01eb908e606d82/4",
    "crc32": "00000000",
    "scope": "p",
    "origo": "a0369fd807c2",
    "group_id": 761464,
    "md5": "08db8cb3bf24dc360906fb5e1f33c230"
}
_case_2 = [_phy]

_phy_ = copy.copy(_phy)
_phy_['is_del'] = 1
_phy_['phy_ts'] += sec_10_ns
_case_2.append(_phy_)


# deleted then add
_phy = {
    "size": 2192284,
    "sha1": "00000079840e3bc1a1bf5ee4557d8c0d91de8921",
    "ver": 1501809028041000101,
    "phy_ts": 1501809028474000101,
    "is_del": 0,
    "ts": 1501809028474000101,
    "bucket_id": 1570000000000000062,
    "key": "etlbaishan.20170608-04.task_KafkaDumpHugeA_1496865609344_233_1.parquet",
    "crc32": "00000000",
    "scope": "u",
    "origo": "a0369fd807c2",
    "group_id": 665171,
    "md5": "d77277ab34989bbaf605e306a1cb8a73"
}
_case_3 = [_phy]

_phy_ = copy.copy(_phy)
_phy_['is_del'] = 1
_phy_['phy_ts'] += sec_10_ns
_case_3.append(_phy_)

_phy_ = copy.copy(_phy)
_phy_['ts'] += sec_10_ns
_phy_['phy_ts'] = _phy_['ts']
_case_3.append(_phy_)


# multi keys
_phy = {
    "size": 57689,
    "sha1": "000001b7b2448cbd351ba9cec1b88e8f37768661",
    "ver": 1502133235007000101,
    "phy_ts": 1502133235495000101,
    "is_del": 0,
    "ts": 1502133235495000101,
    "bucket_id": 1570000000000000062,
    "key": "etlbaishan.20170606-11.task_KafkaDumpTencent_1496717948166_345_1.parquet",
    "crc32": "00000000",
    "scope": "u",
    "origo": "a0369fd807c2",
    "group_id": 667541,
    "md5": "28e2b14453380051f9fc98fdd7c92278"
}
_case_4 = []

for i in xrange(0, 10):
    _phy_ = copy.copy(_phy)
    _phy_['key'] += '_' + str(i)
    _phy_['ts'] += sec_10_ns*i
    _phy_['phy_ts'] = _phy_['ts']
    _case_4.append(_phy_)


def make_phy_iter(case):
    for phy in case:
        yield phy


def _make_referrer(scope, refkey, ver, is_del):
    return needle_source.Referrer(Scope=scope,
                                  RefKey=refkey, Ver=ver, IsDel=is_del)

n0 = {
    'NeedleID': '1',
    'Size': 10,
    'Url': '/',
    'Referrers': [
            _make_referrer('3copy', 'key1', 123, 1),
            _make_referrer('3copy', 'key2', 123, 1),
            _make_referrer('3copy', 'key3', 123, 1),
    ]}

n1 = {
    'NeedleID': '1',
    'Size': 10,
    'Url': '/',
    'Referrers': [
            _make_referrer('3copy', 'key1', 123, 0),
            _make_referrer('3copy', 'key2', 123, 0),
            _make_referrer('3copy', 'key4', 123, 0),
    ]}

n2 = {
    'NeedleID': '1',
    'Size': 10,
    'Url': '/',
    'Referrers': [
            _make_referrer('3copy', 'key3', 123, 0),
            _make_referrer('3copy', 'key5', 123, 0),
            _make_referrer('3copy', 'key6', 123, 1),
    ]}

n3 = {
    'NeedleID': '2',
    'Size': 10,
    'Url': '/',
    'Referrers': [
            _make_referrer('3copy', 'key1', 123, 1),
            _make_referrer('3copy', 'key6', 123, 1),
    ]}

n4 = {
    'NeedleID': 2,
    'Size': 10,
    'Url': '/',
    'Referrers': [
            _make_referrer('3copy', 'key1', 123, 0),
            _make_referrer('3copy', 'key6', 123, 0),
    ]}

class TestNeedleSource(unittest.TestCase):

    def setUp(self):

        self.importer = imports2.Importer({
            'needle_scope': 'sys',
            'front': {
                'host': 'phy-sys.bscstorage.com',
                'accesskey': 'accesskey',
                'secretkey': 'secretkey',
            },
            'etcd': {},
        })
        # for testing
        self.importer.make_list_range = lambda x: x
        self.importer.list_phys_iter = make_phy_iter

    def test_is_pair_referrer(self):

        ref_1 = self.importer.make_referrer(_case_1[0])
        ref_2 = self.importer.make_referrer(_case_1[0])
        self.assertFalse(ref_1.is_pair(ref_2))

        ref_1 = self.importer.make_referrer(_case_2[0])
        ref_2 = self.importer.make_referrer(_case_2[1])
        self.assertTrue(ref_1.is_pair(ref_2))

        ref_1 = self.importer.make_referrer(_case_3[1])
        ref_2 = self.importer.make_referrer(_case_3[0])
        self.assertTrue(ref_1.is_pair(ref_2))

        ref_1 = self.importer.make_referrer(_case_3[1])
        ref_2 = self.importer.make_referrer(_case_3[2])
        self.assertFalse(ref_1.is_pair(ref_2))

    def test_needle_source_iter(self):

        # empty iter
        needles = [x for x in self.importer.needle_source_iter([])]
        self.assertEqual(len(needles), 0)

        for case, n in (
            (_case_1, 1),
            (_case_2, 1),
            (_case_3, 1),
            (_case_4, 1),
            (_case_1+_case_2, 2),
            (_case_2+_case_3+_case_4, 3),
            ):

            needles = [x for x in self.importer.needle_source_iter(case)]
            self.assertEqual(len(needles), n)

            for needle in needles:
                self.assertIsInstance(needle, needle_source.NeedleSource)

    def test_add_referrer(self):

        needle_src = self.importer.new_needle_source(_case_2[0])
        self.assertTrue(len(needle_src['Referrers']), 1)

        self.assertRaises(ValueError, needle_src.add_referrer, 0)
        self.assertRaises(ValueError, needle_src.add_referrer, 'referrer')
        self.assertRaises(ValueError, needle_src.add_referrer, _case_2[1])

        needle_src.add_referrer(self.importer.make_referrer(_case_2[1]))
        self.assertTrue(len(needle_src['Referrers']), 1)

    def test_needle_id_less_than(self):

        needles = []
        for case in (_case_1, _case_2, _case_3, _case_4):
            needles.extend(self.importer.needle_source_iter(case))

        for i in xrange(len(needles)):
            for j in xrange(i+1, len(needles)):
                self.assertLess(needles[i], needles[j])

    def test_needle_source_referrer_len(self):

        for case, n in (
            (_case_1, 1),
            (_case_2, 1),
            (_case_3, 2),
            (_case_4, 10),
            ):

            needles = [x for x in self.importer.needle_source_iter(case)]
            self.assertEqual(len(needles[0]['Referrers']), n)

    def test_needle_source_referrer_value(self):

        def _assert(referrer, phy):
            self.assertEqual(referrer['Scope'], self.importer.needle_scope)
            self.assertEqual(referrer['RefKey'],
                             '{bucket_id}/{scope}/{key}'.format(**phy))
            self.assertEqual(referrer['Ver'],   phy['ts'])
            self.assertEqual(referrer['IsDel'], phy['is_del'])

        needle_src = [x for x in self.importer.needle_source_iter(_case_1)][0]
        _assert(needle_src['Referrers'][0], _case_1[0])

        needle_src = [x for x in self.importer.needle_source_iter(_case_2)][0]
        _assert(needle_src['Referrers'][0], _case_2[1])

        needle_src = [x for x in self.importer.needle_source_iter(_case_3)][0]
        _assert(needle_src['Referrers'][0], _case_3[1])
        _assert(needle_src['Referrers'][1], _case_3[2])

        needle_src = [x for x in self.importer.needle_source_iter(_case_4)][0]

        for i in xrange(len(_case_4)):
            _assert(needle_src['Referrers'][i], _case_4[i])

    def test_merge_referrer(self):

        n012 = {
            'NeedleID': '1',
            'Size': 10,
            'Url': '/',
            'Referrers': [
                    _make_referrer('3copy', 'key1', 123, 1),
                    _make_referrer('3copy', 'key2', 123, 1),
                    _make_referrer('3copy', 'key3', 123, 1),
                    _make_referrer('3copy', 'key4', 123, 0),
                    _make_referrer('3copy', 'key5', 123, 0),
                    _make_referrer('3copy', 'key6', 123, 1),
            ]}

        n012_del = {
            'NeedleID': '1',
            'Size': 10,
            'Url': '/',
            'Referrers': [
                    _make_referrer('3copy', 'key4', 123, 0),
                    _make_referrer('3copy', 'key5', 123, 0),
            ]}

        ndl_src0 =       needle_source.NeedleSource(n0)
        ndl_src1 =       needle_source.NeedleSource(n1)
        ndl_src2 =       needle_source.NeedleSource(n2)
        ndl_src012 =     needle_source.NeedleSource(n012)
        ndl_src012_del = needle_source.NeedleSource(n012_del)
        ndl_src3 =       needle_source.NeedleSource(n3)

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

        self.assertRaises(needle_source.NeedleIdNotEqual, needle_source.merge_referrer, [ndl_src2, ndl_src3])

    def test_merge_needle_src_iters(self):
        self.maxDiff = None

        expected = [
                {
                    'NeedleID': '1',
                    'Size': 10,
                    'Url': '/',
                    'Referrers': [
                        _make_referrer('3copy', 'key1', 123, 1),
                        _make_referrer('3copy', 'key2', 123, 1),
                        _make_referrer('3copy', 'key3', 123, 1),
                        _make_referrer('3copy', 'key4', 123, 0),
                        _make_referrer('3copy', 'key5', 123, 0),
                        _make_referrer('3copy', 'key6', 123, 1),
                        ]
                },
                {
                    'NeedleID': '2',
                    'Size': 10,
                    'Url': '/',
                    'Referrers': [
                        _make_referrer('3copy', 'key1', 123, 1),
                        _make_referrer('3copy', 'key6', 123, 1),
                ]}
            ]

        expected_del = [
                {
                    'NeedleID': '1',
                    'Size': 10,
                    'Url': '/',
                    'Referrers': [
                        _make_referrer('3copy', 'key4', 123, 0),
                        _make_referrer('3copy', 'key5', 123, 0),
                ]},
            ]

        ndls = []
        for n in (n0, n3, n1, n2, n4):
            ndls.append(needle_source.NeedleSource(n))

        res_ndls = []
        for ndl in needle_source.merge_needle_source_iters():
            res_ndls.append(ndl)

        self.assertEqual([], res_ndls)

        res_ndls = []
        for ndl in needle_source.merge_needle_source_iters(ndls[1:2]):
            res_ndls.append(ndl)

        self.assertEqual([ndls[1]], res_ndls)


        res_ndls = []
        for ndl in needle_source.merge_needle_source_iters(ndls[:2], ndls[2:4], ndls[4:]):
            res_ndls.append(ndl)

        self.assertEqual(expected, res_ndls)

        res_ndls = []
        for ndl in needle_source.merge_needle_source_iters(ndls[:2], ndls[2:4]):
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


if __name__ == '__main__':
    unittest.main()
