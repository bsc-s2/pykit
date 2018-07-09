#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import utfjson
from pykit.ectypes import BlockGroupID
from pykit.ectypes import BlockID
from pykit.ectypes import BlockIndex
from pykit.ectypes import DriveID


def id_str(_id): return '"{s}"'.format(s=str(_id))


class TestIDBase(unittest.TestCase):

    def setUp(self):

        self.block_group_id = BlockGroupID('g000640000000123')
        self.block_id = BlockID('d1g0006300000001230101c62d8736c72800020000000001')
        self.block_index = BlockIndex('1234')
        self.drive_id = DriveID('1122334455660001')

    def test_json_dump(self):

        cases = (
            (None, 'null'),
            (self.block_group_id,   id_str(self.block_group_id)),

            (self.block_group_id,   id_str(self.block_group_id)),
            (self.block_id,         id_str(str(self.block_id))),
            (self.block_index,      id_str(self.block_index)),
            (self.drive_id,         id_str(self.drive_id)),

            ([self.block_group_id, self.drive_id],
                "[{0}, {1}]".format(id_str(self.block_group_id), id_str(self.drive_id))),
            ((self.block_group_id, self.drive_id),
                "[{0}, {1}]".format(id_str(self.block_group_id), id_str(self.drive_id))),

            ({'xxx': self.block_id},
                '{{"xxx": {0}}}'.format(id_str(self.block_id))),
            ({10: self.block_id},
                '{{"10": {0}}}'.format(id_str(self.block_id))),

            ({self.block_id: 'abc'},
                '{{{0}: "abc"}}'.format(id_str(self.block_id))),
            ({self.block_group_id: self.block_id},
                '{{{0}: {1}}}'.format(id_str(self.block_group_id), id_str(self.block_id))),
            ({self.block_group_id: (self.block_id, self.drive_id)},
                '{{{0}: [{1}, {2}]}}'.format(id_str(self.block_group_id),
                                             id_str(self.block_id), id_str(self.drive_id))),
        )

        for obj, expected in cases:
            self.assertEqual(expected, utfjson.dump(obj))

    def test_disable_setattr(self):

        with self.assertRaises(TypeError):
            self.block_group_id.block_size = 0

        with self.assertRaises(TypeError):
            self.block_id.drive_id = 0

        with self.assertRaises(TypeError):
            self.block_index.i = 0

        with self.assertRaises(TypeError):
            self.drive_id.server_id = 0

    def test_new(self):

        block_index = BlockIndex('1234')
        self.assertEqual(self.block_index, block_index)

        block_index = BlockIndex('12', '34')
        self.assertEqual(self.block_index, block_index)

        block_index = BlockIndex(i='12', j='34')
        self.assertEqual(self.block_index, block_index)

    def test_new_invalid(self):

        with self.assertRaises(ValueError):
            block_index = BlockIndex('01234')

        with self.assertRaises(ValueError):
            block_index = BlockIndex('012')

        with self.assertRaises(ValueError):
            block_index = BlockIndex(i='01', j='345')
