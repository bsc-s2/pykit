#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit.ectypes import BlockID
from pykit.ectypes import DriveID


class TestBlockID(unittest.TestCase):

    def test_new(self):
        block_id = 'd1g0006300000001230101idc000c62d8736c72800020000000001'

        _bid = BlockID('d1', 'g000630000000123', '0101',
                               DriveID('idc000' 'c62d8736c7280002'), 1)
        self.assertEqual(block_id, str(_bid))

        self.assertEqual(_bid, BlockID(block_id))
        self.assertEqual(_bid, BlockID(_bid))

        bid = BlockID(block_id)

        self.assertEqual('d1', bid.type)
        self.assertEqual('g000630000000123', str(bid.block_group_id))
        self.assertEqual((1, 1), bid.block_index.as_tuple())
        self.assertEqual('0101', str(bid.block_index))
        self.assertEqual('idc000' 'c62d8736c7280002', bid.drive_id)
        self.assertEqual(1, bid.block_id_seq)

    def test_block_id_block_id(self):

        block_id = 'd1g0006300000001230101idc000c62d8736c72800020000000001'
        bid = BlockID('d1', 'g000630000000123', '0101',
                      DriveID('idc000' 'c62d8736c728' '0002'), 1)

        self.assertEqual('d1g0006300000001230101idc000c62d8736c72800020000000001', bid.block_id)
        self.assertEqual(block_id, bid.block_id)
        self.assertIs(bid, bid.block_id)

    def test_block_id_embed(self):

        block_id = 'd1g0006300000001230101idc000c62d8736c72800020000000001'
        bid = BlockID('d1', 'g000630000000123', '0101',
                      DriveID('idc000' 'c62d8736c728' '0002'), 1)

        # embedded drive_id attrs
        self.assertEqual('idc000' 'c62d8736c728', bid.server_id)
        self.assertEqual('002', bid.mountpoint_index)
        self.assertEqual(6002, bid.port)

        # embedded server_id attrs
        self.assertEqual('idc000', bid.idc_id)
        self.assertEqual('c62d8736c728', bid.mac_addr)

    def test_new_invalid(self):

        block_id_invalid = 'd1g0006300000001230101idc000c62d8736c728000200000'
        self.assertRaises(ValueError, BlockID, block_id_invalid)

    def test_tostr(self):

        block_id = 'd1g0006300000001230101idc000c62d8736c72800020000000001'

        bid = BlockID(block_id)

        self.assertEqual(block_id, str(bid))
        self.assertEqual(block_id, '{0}'.format(bid))
        self.assertEqual("'d1g0006300000001230101idc000c62d8736c72800020000000001'", repr(bid))
