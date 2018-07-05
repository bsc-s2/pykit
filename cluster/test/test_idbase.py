#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit.cluster import BlockGroupID
from pykit.cluster import BlockID
from pykit.cluster import BlockIndex
from pykit.cluster import DriveID
from pykit.cluster import json_dump


def id_str(_id): return '"{s}"'.format(s=str(_id))


class TestIDBase(unittest.TestCase):

    def setUp(self):

        self.block_group_id = BlockGroupID.parse('g000640000000123')
        self.block_id = BlockID.parse('d1g0006300000001230101c62d8736c72800020000000001')
        self.block_index = BlockIndex.parse('1234')
        self.drive_id = DriveID.parse('1122334455660001')

    def test_json_dump(self):

        cases = (
            (None, 'null'),
            (self.block_group_id.tostr(), id_str(self.block_group_id)),

            (self.block_group_id,   id_str(self.block_group_id)),
            (self.block_id,         id_str(str(self.block_id))),
            (self.block_index,      id_str(self.block_index.tostr())),
            (self.drive_id,         id_str(self.drive_id)),

            ([self.block_group_id, self.drive_id],
             "[{0}, {1}]".format(id_str(self.block_group_id), id_str(self.drive_id))),
            ((self.block_group_id, self.drive_id),
                "[{0}, {1}]".format(id_str(self.block_group_id), id_str(self.drive_id))),

            ({'xxx': self.block_id}, '{{"xxx": {0}}}'.format(id_str(self.block_id))),
            ({10: self.block_id}, '{{"10": {0}}}'.format(id_str(self.block_id))),

            ({self.block_id: 'abc'}, '{{{0}: "abc"}}'.format(id_str(self.block_id))),
            ({self.block_group_id: self.block_id},
                '{{{0}: {1}}}'.format(id_str(self.block_group_id), id_str(self.block_id))),
            ({self.block_group_id: (self.block_id, self.drive_id)},
                '{{{0}: [{1}, {2}]}}'.format(id_str(self.block_group_id),
                                             id_str(self.block_id), id_str(self.drive_id))),
        )

        for obj, excepted in cases:
            self.assertEqual(json_dump(obj), excepted)
