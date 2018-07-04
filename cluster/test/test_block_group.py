#!/usr/bin/env python2
# coding: utf-8

import copy
import unittest

from pykit import cluster
from pykit import ututil
from pykit.cluster import BlockDesc
from pykit.cluster import BlockGroup
from pykit.cluster import BlockNotFoundError

dd = ututil.dd

_ec_config = {
    'in_idc': [4, 2],
    'cross_idc': [2, 1],
    'ec_policy': 'lrc',
    'data_replica': 3
}

_empty_group = BlockGroup({
    'bg_seq': 0,
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

    def test_parse(self):
        block_group_id = 'g000640000000123'

        bgid = cluster.BlockGroupID(64, 123)
        self.assertEqual(block_group_id, str(bgid))

        bgid = cluster.BlockGroupID.parse(block_group_id)
        self.assertEqual((64, 123), bgid)

        bgid = cluster.BlockGroupID.parse(bgid)
        self.assertEqual((64, 123), bgid)

    def test_invalid(self):

        # test invalid input
        block_group_id_invalid = 'g00064000000012345'
        self.assertRaises(cluster.BlockGroupIDError,
                          cluster.BlockGroupID.parse, block_group_id_invalid)

    def test_tostr(self):
        block_group_id = 'g000640000000123'
        bgid = cluster.BlockGroupID.parse(block_group_id)
        self.assertEqual(block_group_id, str(bgid))
        self.assertEqual(block_group_id, bgid.tostr())
        self.assertEqual(block_group_id, '{0}'.format(bgid))
        self.assertEqual(
            "_BlockGroupID(block_size=64, seq=123)", repr(bgid))


class TestClusterBlockGroup(unittest.TestCase):

    def setUp(self):
        self.foo_block = BlockDesc({
            'block_id': cluster.BlockID('d0',
                                        'g000640000000123',
                                        '0000',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
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

    def test_new_deref_config(self):

        cnf = copy.deepcopy(_ec_config)
        b = BlockGroup(block_group_id='g000640000000123',
                       config=cnf,
                       idcs=['a', 'b', 'c'])

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

        with self.assertRaises(cluster.BlockNotFoundError):
            g.get_block('9999', raise_error=True)

        new_block = {
            'block_id': cluster.BlockID('d0',
                                        'g000640000000123',
                                        '0000',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1),
            'size': 1000,
            'range': ['0a', '0b'],
            'is_del': 0
        }

        g.replace_block(new_block)
        block = g.get_block(new_block['block_id'].block_index)
        self.assertDictEqual(new_block, block)

        with self.assertRaises(cluster.BlockNotFoundError):
            g.get_block('0002', raise_error=True)

        with self.assertRaises(cluster.BlockIndexError):
            g.get_block('d0g0006400000001230000c62d2')

    def test_mark_delete_block(self):
        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)
        new_block = {
            'block_id': cluster.BlockID('d0',
                                        'g000640000000123',
                                        '0000',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'range': ['0a', '0b'],
            'is_del': 0
        }

        g.replace_block(new_block)
        g.mark_delete_block('0000')
        block = g.get_block('0000')

        self.assertEqual(1, block['is_del'])

        self.assertRaises(BlockNotFoundError, g.mark_delete_block, '9999')

    def test_delete_block(self):

        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)
        self.assertIsNone(g.get_block('0000'))

        g.replace_block(self.foo_block)
        self.assertIsNotNone(g.get_block('0000'))

        g.delete_block('0000')
        self.assertIsNone(g.get_block('0000'))

        g.delete_block('0000')
        self.assertIsNone(g.get_block('0000'))

    def test_replace_block(self):

        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)

        prev = g.replace_block(self.foo_block)
        self.assertIsNone(prev)

        block = g.get_block('0000')
        self.assertEqual(0, block['is_del'])

        prev = g.replace_block(self.foo_block)
        self.assertEqual(self.foo_block, prev)

    def test_get_free_block_index(self):
        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)

        new_block = {
            'block_id': cluster.BlockID('d0',
                                        'g000640000000123',
                                        '0000',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1),
            'size': 1000,
            'range': ['0a', '0b'],
            'is_del': 0
        }

        g.replace_block(new_block)

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

        self.assertRaises(cluster.BlockTypeNotSupported, g.get_block_type, '0299')
        self.assertRaises(cluster.BlockTypeNotSupported, g.get_block_type, '0900')

    def test_get_block_idc(self):
        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)

        self.assertEqual('a', g.get_block_idc('0000'))
        self.assertEqual('b', g.get_block_idc('0100'))
        self.assertEqual('c', g.get_block_idc('0200'))

        d0 = {
            'block_id': cluster.BlockID('d0',
                                        'g000640000000123',
                                        '0000',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1),
            'size': 1000,
            'range': ['0a', '0b'],
            'is_del': 0
        }
        g.replace_block(d0)
        self.assertEqual('a', g.get_block_idc('0000'))

    def test_get_replica_index_not_include_me(self):
        g = BlockGroup(block_group_id='g000640000000123', idcs=['a', 'b', 'c'], config=_ec_config)
        self.assertEqual(['0006', '0010'], g.get_replica_indexes('0000', include_me=False))
        self.assertEqual(['0000', '0010'], g.get_replica_indexes('0006', include_me=False))
        self.assertEqual(['0000', '0006'], g.get_replica_indexes('0010', include_me=False))

        with self.assertRaises(cluster.BlockTypeNotSupportReplica):
            g.get_replica_indexes('0004', include_me=False)

        with self.assertRaises(cluster.BlockTypeNotSupportReplica):
            g.get_replica_indexes('0204', include_me=False)
