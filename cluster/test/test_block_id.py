#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import cluster


class TestClusterBlock(unittest.TestCase):

    def test_parse_and_print(self):

        block_id = 'd1g0006300000001230101c62d8736c72800020000000001'

        bid = cluster.BlockID('d1', 'g000630000000123', '0101', cluster.DriveID.parse('c62d8736c7280002'), 1)
        self.assertEqual(block_id, str(bid))

        bid = cluster.BlockID.parse(block_id)

        self.assertEqual('d1', bid.type)
        self.assertEqual('g000630000000123', str(bid.block_group_id))
        self.assertEqual((1, 1), bid.block_index)
        self.assertEqual('0101', str(bid.block_index))
        self.assertEqual('c62d8736c7280002', bid.drive_id.tostr())
        self.assertEqual(1, bid.bg_seq)

        self.assertEqual(block_id, str(bid))
        self.assertEqual(block_id, '{0}'.format(bid))
        self.assertEqual(
            "_BlockID(type='d1', block_group_id=_BlockGroupID(block_size=63, seq=123), block_index=_BlockIndex(i=1, j=1), drive_id=_DriveID(server_id='c62d8736c728', mountpoint_index=2), bg_seq=1)",
            repr(bid))

        # test invalid input
        block_id_invalid = 'd1g0006300000001230101c62d8736c728000200000'
        self.assertRaises(cluster.BlockIDError,
                          cluster.BlockID.parse, block_id_invalid)

    def test_new(self):

        block_id = 'd1g0006300000001230101c62d8736c72800020000000001'

        # new with string drive id

        bid = cluster.BlockID('d1', 'g000630000000123', '0101', 'c62d8736c7280002', 1)
        self.assertEqual(block_id, str(bid))

        self.assertIsInstance(bid.drive_id, cluster.DriveID)

    def test_tostr(self):

        block_id = 'd1g0006300000001230101c62d8736c72800020000000001'
        bid = cluster.BlockID.parse(block_id)

        self.assertEqual(block_id, bid.tostr())
        self.assertEqual(block_id, str(bid))

        self.assertIsInstance(bid.drive_id, cluster.DriveID)
        self.assertEqual('c62d8736c7280002', str(bid.drive_id))
        self.assertEqual('c62d8736c7280002', bid.drive_id.tostr())
        self.assertEqual('c62d8736c728', bid.drive_id.server_id)
