#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import ectypes
from pykit.ectypes import BlockID


class TestBlockID(unittest.TestCase):

    def test_parse(self):
        block_id = 'd1g0006300000001230101c62d8736c72800020000000001'

        _bid = ectypes.BlockID('d1', 'g000630000000123', '0101',
                               ectypes.DriveID.parse('c62d8736c7280002'), 1)
        self.assertEqual(block_id, str(_bid))

        self.assertEqual(_bid, BlockID.parse(block_id))
        self.assertEqual(_bid, BlockID.parse(_bid))

        bid = ectypes.BlockID.parse(block_id)

        self.assertEqual('d1', bid.type)
        self.assertEqual('g000630000000123', str(bid.block_group_id))
        self.assertEqual((1, 1), bid.block_index)
        self.assertEqual('0101', str(bid.block_index))
        self.assertEqual('c62d8736c7280002', bid.drive_id.tostr())
        self.assertEqual(1, bid.block_id_seq)

        # test invalid input
        block_id_invalid = 'd1g0006300000001230101c62d8736c728000200000'
        self.assertRaises(ectypes.BlockIDError,
                          ectypes.BlockID.parse, block_id_invalid)

    def test_print(self):

        block_id = 'd1g0006300000001230101c62d8736c72800020000000001'

        bid = ectypes.BlockID.parse(block_id)

        self.assertEqual(block_id, str(bid))
        self.assertEqual(block_id, '{0}'.format(bid))
        self.assertEqual(
            "_BlockID(type='d1', block_group_id=_BlockGroupID(block_size=63, seq=123), block_index=_BlockIndex(i=1, j=1), drive_id=_DriveID(server_id='c62d8736c728', mountpoint_index=2), block_id_seq=1)",
            repr(bid))

    def test_new(self):

        block_id = 'd1g0006300000001230101c62d8736c72800020000000001'

        # new with string drive id

        bid = ectypes.BlockID('d1', 'g000630000000123',
                              '0101', 'c62d8736c7280002', 1)
        self.assertEqual(block_id, str(bid))

        self.assertIsInstance(bid.drive_id, ectypes.DriveID)

    def test_tostr(self):

        block_id = 'd1g0006300000001230101c62d8736c72800020000000001'
        bid = ectypes.BlockID.parse(block_id)

        self.assertEqual(block_id, bid.tostr())
        self.assertEqual(block_id, str(bid))

        self.assertIsInstance(bid.drive_id, ectypes.DriveID)
        self.assertEqual('c62d8736c7280002', str(bid.drive_id))
        self.assertEqual('c62d8736c7280002', bid.drive_id.tostr())
        self.assertEqual('c62d8736c728', bid.drive_id.server_id)
