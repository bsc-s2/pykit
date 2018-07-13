#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import ututil
from pykit.ectypes import MountPointIndex

dd = ututil.dd


class TestMountPointIndex(unittest.TestCase):

    def test_mount_point_id(self):

        cases = (
            ('001', 1),
            ('010', 10),
            ('100', 100),
            ('999', 999),
            ('999', '999'),
            ('001', '001'),
            ('010', '010'),
        )

        for result, mp_inx in cases:
            mount_point_index = MountPointIndex(mp_inx)
            self.assertEqual(result, mount_point_index)

    def test_validate_mount_point_index(self):

        invalid_cases = (
            (),
            [],
            {},
            'foo',
            1000,
            -1,
            '1000'
            '-1'
        )

        for c in invalid_cases:
            self.assertRaises(ValueError, MountPointIndex, c)
