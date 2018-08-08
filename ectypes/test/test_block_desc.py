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
                   'is_del': 0}),

                 ({'block_id': block_id,
                   'range': ['a', 'b'],
                   'size': 34,
                   'is_del': 0},
                  {'block_id': BlockID(block_id),
                   'range': rangeset.Range('a', 'b'),
                   'size': 34,
                   'is_del': 0}),

                 ({'block_id': BlockID(block_id),
                   'range': rangeset.Range('b', 'bb')},
                  {'block_id': BlockID(block_id),
                   'range': rangeset.Range('b', 'bb'),
                   'size': 0,
                   'is_del': 0, })
                 )

        for b, expected in cases:
            if b is None:
                blk = BlockDesc()
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
            'is_del': 0
        })

        rst = utfjson.dump(blk)
        expected = ('{"is_del": 0, "range": ["0a", "0b"], "block_id": '
                    '"d0g0006400000001230000idc000c62d8736c72800020000000001", "size": 1000}')

        self.assertEqual(expected, rst)
        loaded = BlockDesc(utfjson.load(rst))
        self.assertEqual(blk, loaded)
