#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import cluster


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
