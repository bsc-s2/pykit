#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import utfjson
from pykit.ectypes import BlockGroupID
from pykit.ectypes import BlockID
from pykit.ectypes import BlockIndex
from pykit.ectypes import DriveID
from pykit.ectypes import IDBase


def id_str(_id): return '"{s}"'.format(s=str(_id))


class TestIDBase(unittest.TestCase):

    def setUp(self):

        self.block_group_id = BlockGroupID('g000640000000123')
        self.block_id = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000001')
        self.block_index = BlockIndex('1234')
        self.drive_id = DriveID('idc000' '1122334455660001')

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


class SubID1(IDBase):
    _attrs = (
        ('a',  0,  1, lambda x: 1),
    )
    _str_len = 1


class SubID2(IDBase):
    _attrs = (
        ('b',  0,  1, lambda x: 2),
    )
    _str_len = 1

class NonKeyID(IDBase):
    _attrs = (
        ('foo',  0,  1, str),
        ('sub1', 1,  2, SubID1, 'embed'),
        ('sub2', 1,  2, SubID2, {'embed': True, 'key_attr': False}),

        ('bar',  1,  2, str, False),
        ('wow',  1,  2, str, {'key_attr': False}),

        ('me',   1,  2, str, 'self'),
        ('me2',  1,  2, str, {'self': True}),
    )

    _str_len = 2

    _tostr_fmt = '{foo}{sub1}'


class TestNonKeyAttr(unittest.TestCase):

    def test_non_key_attr(self):

        s = NonKeyID('12')
        self.assertEqual(('12', '1', '2', '2', '2'), (s, s.foo, s.sub1, s.bar, s.wow))

        s = NonKeyID('1', '2')
        self.assertEqual(('12', '1', '2', '2', '2'), (s, s.foo, s.sub1, s.bar, s.wow))

        s = NonKeyID('1', sub1='2')
        self.assertEqual(('12', '1', '2', '2', '2'), (s, s.foo, s.sub1, s.bar, s.wow))

        s = NonKeyID(foo='1', sub1='2')
        self.assertEqual(('12', '1', '2', '2', '2'), (s, s.foo, s.sub1, s.bar, s.wow))

    def test_as_tuple(self):
        s = NonKeyID('12')
        self.assertEqual(('1', '2'), s.as_tuple())

    def test_self(self):
        s = NonKeyID('12')
        self.assertIs(s, s.me)
        self.assertIs(s, s.me2)

    def test_embed(self):
        s = NonKeyID('12')
        self.assertEqual(1, s.a)
        self.assertEqual(2, s.b)
