#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import rangeset
from pykit import utfjson
from pykit.ectypes import BlockDesc
from pykit.ectypes import BlockID
from pykit.ectypes import DriveID


class TestBlockDesc(unittest.TestCase):

    def test_blockdesc(self):

        block_id = 'd1g0006300000001230101idc000c62d8736c72800020000000001'
        cases = ((None,
                  {'block_id': None,
                   'size': 0,
                   'range': None,
                   'ts_range': None,
                   'ref_num': 0,
                   'is_del': 0}),

                 ({'block_id': block_id,
                   'range': ['a', 'b'],
                   'ts_range': ["124", None],
                   'ref_num': 0,
                   'size': 34,
                   'mtime': 1,
                   'is_del': 0},
                  {'block_id': BlockID(block_id),
                   'range': rangeset.Range('a', 'b'),
                   'ts_range': ["124", None],
                   'ref_num': 0,
                   'size': 34,
                   'mtime': 1,
                   'is_del': 0}),

                 ({'block_id': BlockID(block_id),
                   'range': rangeset.Range('b', 'bb'),
                   'ts_range': ["1235", "456"],
                   'ref_num': 0,
                   'mtime': 1},
                  {'block_id': BlockID(block_id),
                   'range': rangeset.Range('b', 'bb'),
                   'ts_range': ["1235", "456"],
                   'ref_num': 0,
                   'size': 0,
                   'mtime': 1,
                   'is_del': 0, })
                 )

        for b, expected in cases:
            if b is None:
                blk = BlockDesc()
                expected['mtime'] = blk["mtime"]
            else:
                blk = BlockDesc(b)

            self.assertEqual(expected, blk)

        self.assertRaises(ValueError, BlockDesc, is_del='a')
        self.assertRaises(ValueError, BlockDesc, size='a')
        self.assertRaises(KeyError, BlockDesc, a=3)

    def test_json(self):
        blk = BlockDesc({
            'block_id': BlockID('d0', 'g000640000000123', '0000',
                                    DriveID('idc000' 'c62d8736c7280002'), 1),
            'size': 1000,
            'range': ['0a', '0b'],
            'ts_range': ["1235", "456"],
            'ref_num': 1,
            'is_del': 0,
            'mtime': 1,

        })

        rst = utfjson.dump(blk)

        expected = ('{"block_id": "d0g0006400000001230000idc000c62d8736c72800020000000001", "is_del": 0, "ref_num": 1, "range": ["0a", "0b"], "mtime": 1, "ts_range": ["1235", "456"], "size": 1000}')

        self.assertEqual(expected, rst)
        loaded = BlockDesc(utfjson.load(rst))
        self.assertEqual(blk, loaded)

    def test_ref(self):
        block_id = 'd1g0006300000001230101idc000c62d8736c72800020000000001'
        blk = BlockDesc({
            'block_id': block_id,
            'size': 1000,
            'range': ['0a', '0b'],
            'ts_range': ["1235", "456"],
            'ref_num': 1,
            'is_del': 0,
            'mtime': 1,

        })

        blk.add_ref()
        blk.add_ref()
        self.assertEqual(blk['ref_num'], 3)

        blk.rm_ref()
        self.assertEqual(blk['ref_num'], 2)

        self.assertRaises(ValueError, blk.mark_del)

        blk.rm_ref()
        blk.rm_ref()
        self.assertEqual(blk['ref_num'], 0)
        self.assertTrue(blk.can_del())

        self.assertRaises(ValueError, blk.rm_ref)

        blk.mark_del()
