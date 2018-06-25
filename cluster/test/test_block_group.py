#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import cluster
from pykit import ututil

dd = ututil.dd

_ec_config = {
    'ec': {
        'in_idc': [4, 2],
        'cross_idc': [2, 1],
        'ec_policy': 'lrc',
        'data_replica': 3

    }
}

_empty_bkg = {
    'bg_seq': 0,
    'config': {
        'ec': {
            'in_idc': [4, 2],
            'ec_policy': 'lrc',
            'cross_idc': [2, 1],
            'data_replica': 3
        }
    },
    'blocks': {
        '0000': {'is_del': 1, 'range': [None, None], 'type': 'd0', 'block_id': None, 'size': 0},
        '0001': {'is_del': 1, 'range': [None, None], 'type': 'd0', 'block_id': None, 'size': 0},
        '0002': {'is_del': 1, 'range': [None, None], 'type': 'd0', 'block_id': None, 'size': 0},
        '0003': {'is_del': 1, 'range': [None, None], 'type': 'd0', 'block_id': None, 'size': 0},

        '0004': {'is_del': 1, 'range': [None, None], 'type': 'dp', 'block_id': None, 'size': 0},
        '0005': {'is_del': 1, 'range': [None, None], 'type': 'dp', 'block_id': None, 'size': 0},

        '0100': {'is_del': 1, 'range': [None, None], 'type': 'd0', 'block_id': None, 'size': 0},
        '0101': {'is_del': 1, 'range': [None, None], 'type': 'd0', 'block_id': None, 'size': 0},
        '0102': {'is_del': 1, 'range': [None, None], 'type': 'd0', 'block_id': None, 'size': 0},
        '0103': {'is_del': 1, 'range': [None, None], 'type': 'd0', 'block_id': None, 'size': 0},

        '0104': {'is_del': 1, 'range': [None, None], 'type': 'dp', 'block_id': None, 'size': 0},
        '0105': {'is_del': 1, 'range': [None, None], 'type': 'dp', 'block_id': None, 'size': 0},

        '0200': {'is_del': 1, 'range': [None, None], 'type': 'x0', 'block_id': None, 'size': 0},
        '0201': {'is_del': 1, 'range': [None, None], 'type': 'x0', 'block_id': None, 'size': 0},
        '0202': {'is_del': 1, 'range': [None, None], 'type': 'x0', 'block_id': None, 'size': 0},
        '0203': {'is_del': 1, 'range': [None, None], 'type': 'x0', 'block_id': None, 'size': 0},

        '0204': {'is_del': 1, 'range': [None, None], 'type': 'xp', 'block_id': None, 'size': 0},
        '0205': {'is_del': 1, 'range': [None, None], 'type': 'xp', 'block_id': None, 'size': 0},

    },
    'idcs': ['a', 'b', 'c'],
    'block_group_id': 'g000640000000123'
}


class TestClusterBlockGroup(unittest.TestCase):
    def test_parse_and_print(self):
        block_group_id = 'g000640000000123'

        bgid = cluster.BlockGroupID(64, 123)
        self.assertEqual(block_group_id, str(bgid))

        bgid = cluster.BlockGroupID.parse(block_group_id)

        self.assertEqual(64, bgid.block_size)
        self.assertEqual(123, bgid.seq)

        self.assertEqual(block_group_id, str(bgid))
        self.assertEqual(block_group_id, '{0}'.format(bgid))
        self.assertEqual(
            "_BlockGroupID(block_size=64, seq=123)", repr(bgid))

        # test invalid input
        block_group_id_invalid = 'g00064000000012345'
        self.assertRaises(cluster.BlockGroupIDError,
                          cluster.BlockGroupID.parse, block_group_id_invalid)

    def test_tostr(self):
        block_group_id = 'g000640000000123'
        bgid = cluster.BlockGroupID.parse(block_group_id)
        self.assertEqual(block_group_id, str(bgid))
        self.assertEqual(block_group_id, bgid.tostr())

    def test_make_and_new(self):
        block_group = cluster.BlockGroup.make('g000640000000123', ['a', 'b', 'c'], _ec_config)

        self.assertDictEqual(_empty_bkg, block_group)

        self.assertDictEqual(_empty_bkg, cluster.BlockGroup(block_group))

    def test_get_block(self):
        block_group = cluster.BlockGroup.make('g000640000000123', ['a', 'b', 'c'], _ec_config)

        _, block = block_group.get_block(block_index='0000')

        self.assertDictEqual({
            'block_id': None,
            'is_del': 1,
            'range': [None, None],
            'type': 'd0',
            'size': 0
        }, block)

        _, block = block_group.get_block(block_index='9999')
        self.assertIsNone(block)

        with self.assertRaises(cluster.BlockNotFoundError):
            block_group.get_block(block_index='9999', raise_error=True)

        new_block = {
            'block_id': cluster.BlockID('d0',
                                        'g000640000000123',
                                        '0000',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'type': 'd0',
            'range': ['0a', '0b'],
            'is_del': 0
        }

        block_group.replace_block(new_block, block_index='0000')
        _, block = block_group.get_block(block_id=new_block['block_id'])
        self.assertDictEqual(new_block, block)

        _, block = block_group.get_block(block_id='d0g0006400000001230000c62d8736c72800020000000002')
        self.assertIsNone(block)

        with self.assertRaises(cluster.BlockNotFoundError):
            block_group.get_block(block_id='d0g0006400000001230000c62d8736c72800020000000002', raise_error=True)

        with self.assertRaises(cluster.BlockIDError):
            block_group.get_block(block_id='d0g0006400000001230000c62d2')

    def test_mark_delete_block(self):
        block_group = cluster.BlockGroup.make('g000640000000123', ['a', 'b', 'c'], _ec_config)
        new_block = {
            'block_id': cluster.BlockID('d0',
                                        'g000640000000123',
                                        '0000',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'type': 'd0',
            'range': ['0a', '0b'],
            'is_del': 0
        }

        block_group.replace_block(new_block, block_index='0000')
        block_group.mark_delete_block(block_index='0000')
        _, block = block_group.get_block(block_index='0000')

        self.assertEqual(1, block['is_del'])

    def test_replace_block(self):
        block_group = cluster.BlockGroup.make('g000640000000123', ['a', 'b', 'c'], _ec_config)
        new_block = {
            'block_id': cluster.BlockID('d0',
                                        'g000640000000123',
                                        '0000',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'type': 'd0',
            'range': ['0a', '0b'],
            'is_del': 0
        }

        block_group.replace_block(new_block, block_index='0000')
        _, block = block_group.get_block(block_index='0000')
        self.assertEqual(0, block['is_del'])

    def test_get_free_block_index(self):
        block_group = cluster.BlockGroup.make('g000640000000123', ['a', 'b', 'c'], _ec_config)

        new_block = {
            'block_id': cluster.BlockID('d0',
                                        'g000640000000123',
                                        '0000',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'type': 'd0',
            'range': ['0a', '0b'],
            'is_del': 0
        }

        block_group.replace_block(new_block, block_index='0000')

        self.assertDictEqual({'a': ['0001', '0002', '0003'],
                              'b': ['0100', '0101', '0102', '0103']},
                             block_group.get_free_block_indexes('d0'))

        self.assertDictEqual({'a': ['0004', '0005'],
                              'b': ['0104', '0105']},
                             block_group.get_free_block_indexes('dp'))

        self.assertDictEqual({'c': ['0200', '0201', '0202', '0203'], },
                             block_group.get_free_block_indexes('x0'))

        self.assertDictEqual({'c': ['0204', '0205'], },
                             block_group.get_free_block_indexes('xp'))

    def test_get_block_type(self):
        block_group = cluster.BlockGroup.make('g000640000000123', ['a', 'b', 'c'], _ec_config)

        self.assertEqual('d0', block_group.get_block_type('0000'))
        self.assertEqual('dp', block_group.get_block_type('0004'))
        self.assertEqual('d1', block_group.get_block_type('0006'))

        self.assertEqual('d0', block_group.get_block_type('0100'))
        self.assertEqual('dp', block_group.get_block_type('0104'))
        self.assertEqual('d1', block_group.get_block_type('0106'))

        self.assertEqual('x0', block_group.get_block_type('0200'))
        self.assertEqual('xp', block_group.get_block_type('0204'))

        with self.assertRaises(cluster.BlockTypeNotSupported):
            block_group.get_block_type('0209')

    def test_empty_block(self):
        block_group = cluster.BlockGroup.make('g000640000000123', ['a', 'b', 'c'], _ec_config)

        new_block = {
            'block_id': cluster.BlockID('d0',
                                        'g000640000000123',
                                        '0000',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'type': 'd0',
            'range': ['0a', '0b'],
            'is_del': 0
        }

        block_group.replace_block(new_block, block_index='0000')
        block_group['blocks']['0000'] = block_group.empty_block('0000')
        _, block = block_group.get_block(block_index='0000')

        self.assertDictEqual({
            'block_id': None,
            'is_del': 1,
            'range': [None, None],
            'type': 'd0',
            'size': 0
        }, block)

    def test_get_block_idc(self):
        block_group = cluster.BlockGroup.make('g000640000000123', ['a', 'b', 'c'], _ec_config)

        self.assertEqual('a', block_group.get_block_idc(block_index='0000'))
        self.assertEqual('b', block_group.get_block_idc(block_index='0100'))
        self.assertEqual('c', block_group.get_block_idc(block_index='0200'))

        d0 = {
            'block_id': cluster.BlockID('d0',
                                        'g000640000000123',
                                        '0000',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'type': 'd0',
            'range': ['0a', '0b'],
            'is_del': 0
        }
        block_group.replace_block(d0, block_index='0000')
        self.assertEqual('a', block_group.get_block_idc(block_id=d0['block_id']))

    def test_get_replica_block_index(self):
        block_group = cluster.BlockGroup.make('g000640000000123', ['a', 'b', 'c'], _ec_config)
        self.assertEqual(['0006', '0010'], block_group.get_replica_block_index(block_index='0000'))
        self.assertEqual(['0000', '0010'], block_group.get_replica_block_index(block_index='0006'))
        self.assertEqual(['0000', '0006'], block_group.get_replica_block_index(block_index='0010'))

        with self.assertRaises(cluster.BlockTypeNotSupportReplica):
            block_group.get_replica_block_index(block_index='0004')

        with self.assertRaises(cluster.BlockTypeNotSupportReplica):
            block_group.get_replica_block_index(block_index='0200')

        with self.assertRaises(cluster.BlockTypeNotSupportReplica):
            block_group.get_replica_block_index(block_index='0204')

        d0 = {
            'block_id': cluster.BlockID('d0',
                                        'g000640000000123',
                                        '0000',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'type': 'd0',
            'range': ['0a', '0b'],
            'is_del': 0
        }

        d1 = {
            'block_id': cluster.BlockID('d1',
                                        'g000640000000123',
                                        '0006',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'type': 'd1',
            'range': ['0a', '0b'],
            'is_del': 0
        }

        d2 = {
            'block_id': cluster.BlockID('d2',
                                        'g000640000000123',
                                        '0010',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'type': 'd2',
            'range': ['0a', '0b'],
            'is_del': 0
        }

        dp = {
            'block_id': cluster.BlockID('dp',
                                        'g000640000000123',
                                        '0004',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'type': 'dp',
            'range': ['0a', '0b'],
            'is_del': 0
        }

        x0 = {
            'block_id': cluster.BlockID('x0',
                                        'g000640000000123',
                                        '0200',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'type': 'x0',
            'range': ['0a', '0b'],
            'is_del': 0
        }

        xp = {
            'block_id': cluster.BlockID('xp',
                                        'g000640000000123',
                                        '0204',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'type': 'xp',
            'range': ['0a', '0b'],
            'is_del': 0
        }

        block_group.replace_block(d0, block_index='0000')

        block_group['blocks']['0006'] = d1
        block_group['blocks']['0010'] = d2

        block_group['blocks']['0004'] = dp
        block_group['blocks']['0200'] = x0
        block_group['blocks']['0204'] = xp

        self.assertEqual(['0006', '0010'], block_group.get_replica_block_index(block_id=d0['block_id']))
        self.assertEqual(['0000', '0010'], block_group.get_replica_block_index(block_id=d1['block_id']))
        self.assertEqual(['0000', '0006'], block_group.get_replica_block_index(block_id=d2['block_id']))

        with self.assertRaises(cluster.BlockTypeNotSupportReplica):
            block_group.get_replica_block_index(block_id=dp['block_id'])

        with self.assertRaises(cluster.BlockTypeNotSupportReplica):
            block_group.get_replica_block_index(block_id=x0['block_id'])

        with self.assertRaises(cluster.BlockTypeNotSupportReplica):
            block_group.get_replica_block_index(block_id=xp['block_id'])

    def test_block_group_init(self):
        block_group = cluster.BlockGroup(_empty_bkg)
        new_block = {
            'block_id': cluster.BlockID('d0',
                                        'g000640000000123',
                                        '0000',
                                        cluster.DriveID.parse('c62d8736c7280002'),
                                        1).tostr(),
            'size': 1000,
            'type': 'd0',
            'range': ['0a', '0b'],
            'is_del': 0
        }

        block_group.replace_block(new_block, block_index='0000')
        self.assertNotEqual(_empty_bkg, block_group)

        block_group = cluster.BlockGroup(**_empty_bkg)
        block_group.replace_block(new_block, block_index='0000')
        self.assertNotEqual(_empty_bkg, block_group)

        block_group = cluster.BlockGroup(_empty_bkg, **_empty_bkg)
        block_group.replace_block(new_block, block_index='0000')
        self.assertNotEqual(_empty_bkg, block_group)
