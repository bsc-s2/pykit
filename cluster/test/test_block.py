#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import cluster


class TestClusterBlock(unittest.TestCase):

    def test_parse_and_print(self):

        block_id = 'd1g0006300000001230101c62d8736c72800020000000001'
        bid = cluster.BlockID.parse(block_id)

        self.assertEqual('d1', bid.type)
        self.assertEqual('g000630000000123', bid.block_group_id)
        self.assertEqual('0101', bid.block_index)
        self.assertEqual('c62d8736c7280002', bid.drive_id)
        self.assertEqual('0000000001', bid.pg_seq)

        self.assertEqual(block_id, str(bid))
        self.assertEqual(block_id, '{0}'.format(bid))
        self.assertEqual(
            "_BlockID(type='d1', block_group_id='g000630000000123', block_index='0101', drive_id='c62d8736c7280002', pg_seq='0000000001')", repr(bid))

        # test invalid input
        block_id_invalid = 'd1g0006300000001230101c62d8736c728000200000'
        self.assertRaises(cluster.BlockIDError,
                          cluster.BlockID.parse, block_id_invalid)
