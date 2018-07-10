#!/usr/bin/env python2
# coding: utf-8

import copy
import unittest

from pykit import utfjson
from pykit import ututil
from pykit.ectypes import (
    BlockDesc,
    BlockExists,
    BlockGroup,
    BlockGroupID,
    BlockID,
    BlockNotFoundError,
    BlockTypeNotSupportReplica,
    BlockTypeNotSupported,
    DriveID,
)

dd = ututil.dd

_ec_config = {
    'in_idc': [4, 2],
    'cross_idc': [2, 1],
    'ec_policy': 'lrc',
    'data_replica': 3
}

_empty_group = BlockGroup({
    'config': {
        'in_idc': [4, 2],
        'ec_policy': 'lrc',
        'cross_idc': [2, 1],
        'data_replica': 3
    },
    'blocks': {},
    'idcs': ['a', 'b', 'c'],
    'block_group_id': 'g000640000000123'
})


class TestBlockGroupID(unittest.TestCase):

    def test_new(self):
        block_group_id = 'g000640000000123'

        bgid = BlockGroupID(64, 123)
        self.assertEqual(block_group_id, str(bgid))

        bgid = BlockGroupID(block_group_id)
        self.assertEqual((64, 123), bgid.as_tuple())

        bgid = BlockGroupID(bgid)
        self.assertEqual((64, 123), bgid.as_tuple())

    def test_new_invalid(self):

        block_group_id_invalid = 'g00064000000012345'
        self.assertRaises(ValueError, BlockGroupID, block_group_id_invalid)

    def test_tostr(self):
        block_group_id = 'g000640000000123'
        bgid = BlockGroupID(block_group_id)
        self.assertEqual(block_group_id, str(bgid))
        self.assertEqual(block_group_id, '{0}'.format(bgid))
        self.assertEqual("'g000640000000123'", repr(bgid))


class TestBlockGroup(unittest.TestCase):

    def setUp(self):
        self.foo_block = BlockDesc({
            'block_id': BlockID('d0', 'g000640000000123', '0000',
                                    DriveID('c62d8736c7280002'), 1),
            'size': 1000,
            'range': ['0a', '0b'],
            'is_del': 0
        })

    def test_new(self):
        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)

        self.assertEqual(_empty_group, g)

        # test lacking of arg
        self.assertRaises(TypeError, BlockGroup, block_group_id='g000640000000123', idcs=[])
        self.assertRaises(TypeError, BlockGroup, block_group_id='g000640000000123', config=_ec_config)
        self.assertRaises(TypeError, BlockGroup, idcs=[], config=_ec_config)

    def test_json(self):

        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)

        rst = utfjson.dump(g)
        expected = ('{"config": {"in_idc": [4, 2], "ec_policy": "lrc", "cross_idc": [2, 1], '
                    '"data_replica": 3}, "blocks": {}, "idcs": ["a", "b", "c"], '
                    '"block_group_id": "g000640000000123"}')
        self.assertEqual(expected, rst)

        loaded = BlockGroup(utfjson.load(rst))
        self.assertEqual(g, loaded)

    def test_new_deref_config(self):

        cnf = copy.deepcopy(_ec_config)
        b = BlockGroup(block_group_id='g000640000000123', config=cnf, idcs=['a', 'b', 'c'])

        a = copy.deepcopy(b['config'])
        b['config']['in_idc'] = [10, 11]
        self.assertNotEqual(a, b)

        a = copy.deepcopy(b['config'])
        b['config']['cross_idc'] = [10, 11]
        self.assertNotEqual(a, b)

        a = copy.deepcopy(b['config'])
        b['config']['ec_policy'] = 'foo'
        self.assertNotEqual(a, b)

        a = copy.deepcopy(b['config'])
        b['config']['data_replica'] = 100
        self.assertNotEqual(a, b)

    def test_get_block(self):
        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)

        block = g.get_block('0000')
        self.assertIsNone(block)

        block = g.get_block('9999')
        self.assertIsNone(block)

        with self.assertRaises(BlockNotFoundError):
            g.get_block('9999', raise_error=True)

        g.add_block(self.foo_block)
        block = g.get_block(self.foo_block['block_id'].block_index)
        self.assertDictEqual(self.foo_block, block)

        with self.assertRaises(BlockNotFoundError):
            g.get_block('0002', raise_error=True)

        with self.assertRaises(ValueError):
            g.get_block('d0g0006400000001230000c62d2')

    def test_mark_delete_block(self):
        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)

        g.add_block(self.foo_block)
        g.mark_delete_block('0000')
        block = g.get_block('0000')

        self.assertEqual(1, block['is_del'])
        self.assertRaises(BlockNotFoundError, g.mark_delete_block, '9999')

    def test_delete_block(self):

        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)
        self.assertIsNone(g.get_block('0000'))

        g.add_block(self.foo_block)
        self.assertIsNotNone(g.get_block('0000'))

        g.delete_block('0000')
        self.assertIsNone(g.get_block('0000'))

        g.delete_block('0000')
        self.assertIsNone(g.get_block('0000'))

    def test_replace_block(self):

        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)

        prev = g.add_block(self.foo_block)
        self.assertIsNone(prev)

        block = g.get_block('0000')
        self.assertEqual(0, block['is_del'])

        prev = g.add_block(self.foo_block, replace=True)
        self.assertEqual(self.foo_block, prev)

        self.assertRaises(BlockExists, g.add_block, self.foo_block)
        self.assertRaises(BlockExists, g.add_block, self.foo_block, replace=False)

    def test_get_free_block_index(self):

        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)
        g.add_block(self.foo_block)

        self.assertDictEqual({'a': ['0001', '0002', '0003'],
                              'b': ['0100', '0101', '0102', '0103']},
                             g.get_free_block_indexes('d0'))

        self.assertDictEqual({'a': ['0004', '0005'],
                              'b': ['0104', '0105']},
                             g.get_free_block_indexes('dp'))

        self.assertDictEqual({'c': ['0200', '0201', '0202', '0203'], },
                             g.get_free_block_indexes('x0'))

        self.assertDictEqual({'c': ['0204', '0205'], },
                             g.get_free_block_indexes('xp'))

        self.assertDictEqual(
            {
                'a': ['0001', '0002', '0003'],
                'b': ['0100', '0101', '0102', '0103'],
                'c': [],
            },
            g.get_free_block_indexes('d0', get_all=True))

        self.assertDictEqual(
            {
                'a': ['0004', '0005'],
                'b': ['0104', '0105'],
                'c': [],
            },
            g.get_free_block_indexes('dp', get_all=True))

        self.assertDictEqual(
            {
                'a': [],
                'b': [],
                'c': ['0200', '0201', '0202', '0203'],
            },
            g.get_free_block_indexes('x0', get_all=True))

        self.assertDictEqual(
            {
                'a': [],
                'b': [],
                'c': ['0204', '0205'],
            },
            g.get_free_block_indexes('xp', get_all=True))

    def test_get_block_type(self):
        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)

        self.assertEqual('d0', g.get_block_type('0000'))
        self.assertEqual('dp', g.get_block_type('0004'))
        self.assertEqual('d1', g.get_block_type('0006'))
        self.assertEqual('d0', g.get_block_type('0100'))
        self.assertEqual('dp', g.get_block_type('0104'))
        self.assertEqual('d1', g.get_block_type('0106'))
        self.assertEqual('x0', g.get_block_type('0200'))
        self.assertEqual('xp', g.get_block_type('0204'))

        self.assertRaises(BlockTypeNotSupported, g.get_block_type, '0299')
        self.assertRaises(BlockTypeNotSupported, g.get_block_type, '0900')

    def test_get_block_idc(self):
        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)

        self.assertEqual('a', g.get_block_idc('0000'))
        self.assertEqual('b', g.get_block_idc('0100'))
        self.assertEqual('c', g.get_block_idc('0200'))

        d0 = BlockDesc({
            'block_id': BlockID('d0', 'g000640000000123', '0000',
                                    DriveID('c62d8736c7280002'), 1),
            'size': 1000,
            'range': ['0a', '0b'],
            'is_del': 0
        })
        g.add_block(d0)
        self.assertEqual('a', g.get_block_idc('0000'))

    def test_get_replica_index_not_include_me(self):
        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)
        self.assertEqual(['0006', '0010'], g.get_replica_indexes('0000', include_me=False))
        self.assertEqual(['0000', '0010'], g.get_replica_indexes('0006', include_me=False))
        self.assertEqual(['0000', '0006'], g.get_replica_indexes('0010', include_me=False))

        with self.assertRaises(BlockTypeNotSupportReplica):
            g.get_replica_indexes('0004', include_me=False)

        with self.assertRaises(BlockTypeNotSupportReplica):
            g.get_replica_indexes('0204', include_me=False)

    def test_classify_blocks(self):

        gid = 'g000640000000123'

        g = BlockGroup(block_group_id=gid, idcs=['a', 'b', 'c'], config=_ec_config)

        blks = g.classify_blocks(0, only_primary=True)
        self.assertEqual([], blks['ec'] + blks['replica'] + blks['mark_del'])

        base_blk = BlockDesc({
            'size': 1000,
            'range': ['0a', '0b'],
            'is_del': 0
        })

        ec_blk_idxes = ['0000', '0001']
        replica_blk_idxes = ['0002', '0008', '0012']
        mark_del_idxes = ['0003', '0004']

        for i, idx in enumerate(ec_blk_idxes + replica_blk_idxes + mark_del_idxes):

            typ = g.get_block_type(idx)

            blkid = BlockID(typ, gid, idx, DriveID('c62d8736c7280002'), i)

            blk = copy.deepcopy(base_blk)

            blk['block_id'] = blkid

            if idx in mark_del_idxes:
                blk['is_del'] = 1

            g.add_block(blk)

        for only_primary in (True, False):

            blks = g.classify_blocks(0, only_primary)

            blk_idxes = []

            for blk in blks['ec'] + blks['replica'] + blks['mark_del']:
                idx = BlockID(blk['block_id']).block_index
                blk_idxes.append(idx)

            expect_ids = copy.deepcopy(ec_blk_idxes)

            #'0004' in ec_blk_idxes is parity, so should not in mark_del
            if only_primary is True:
                expect_ids += replica_blk_idxes[:1] + mark_del_idxes[:1]
            else:
                expect_ids += replica_blk_idxes + mark_del_idxes[:1]

            self.assertEqual(expect_ids, blk_idxes)

    def test_get_parities(self):

        gid = 'g000640000000123'

        g = BlockGroup(block_group_id=gid, idcs=['a', 'b', 'c'], config=_ec_config)

        parities = g.get_parities(idc_index=0)
        self.assertEqual([], parities)

        base_parity = BlockDesc({
            'size': 1000,
            'range': ['0a', '0b'],
            'is_del': 0
        })

        parity_idxes = ['0004', '0005']

        for i, idx in enumerate(parity_idxes):

            blkid = BlockID('dp', gid, idx, DriveID('c62d8736c7280002'), i)

            parity = copy.deepcopy(base_parity)

            parity['block_id'] = blkid

            g.add_block(parity)

        idxes = g.get_parity_indexes(idc_index=0)
        self.assertEqual(parity_idxes, idxes)

        parities = g.get_parities(idc_index=0)

        idxes = []
        for p in parities:
            idx = BlockID(p['block_id']).block_index
            idxes.append(idx)

        self.assertEqual(parity_idxes, idxes)
