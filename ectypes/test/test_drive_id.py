#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import ectypes
from pykit import ututil
from pykit.ectypes import DriveID

dd = ututil.dd


class TestDriveID(unittest.TestCase):

    def test__drive_id(self):
        cases = (
            ('112233445566', 1),
            ('112233445566', 10),
            ('112233445566', 100),
            ('112233445566', 999),

            ('aabbccddeeff', 1),
            ('aabbccddeeff', 10),
            ('aabbccddeeff', 100),
            ('aabbccddeeff', 999),

            ('1122ccddeeff', 1),
            ('1122ccddeeff', 10),
            ('1122ccddeeff', 100),
            ('1122ccddeeff', 999),
        )

        for sid, mp_idx in cases:
            drive_id = DriveID(sid, mp_idx)
            self.assertEqual(sid, drive_id.server_id)
            self.assertEqual('%03d' % mp_idx, drive_id.mountpoint_index)
            self.assertEqual(mp_idx, int(drive_id.mountpoint_index))
            self.assertEqual('%s0%03d' % (sid[:12], mp_idx % 1000), drive_id)

            drvid = DriveID(drive_id)
            self.assertEqual(sid, drvid.server_id)
            self.assertEqual(drvid, DriveID(drvid))

    def test_drive_id_server_id(self):

        for drive_id in (DriveID('112233445566', 1),
                         DriveID('1122334455660001')):

            dd(drive_id)

            self.assertIsInstance(drive_id.server_id, str)
            self.assertEqual('112233445566', drive_id.server_id)
            self.assertEqual('1122334455660001', str(drive_id))

    def test_validate_drive_id(self):
        invalid_cases = (
            (),
            [],
            {},
            'foo',
            123,
            'aabbccddeeff*001',
            'aabbccddeeff000a',
            '*&bbccddeeff0001',
            'AAbbccddeeff0001',
            'AAbbccddeeff0xxx',
        )

        for c in invalid_cases:
            dd(c)
            self.assertRaises(ValueError, ectypes.DriveID, c)

        cases = (
            'aabbccddeeff0001',
            'aabbccddeeff0100',
            'aabbccddeeff0999',
            '11bbccddeeff0999',
            '11bb33ddeeff0999',
        )

        for c in cases:
            ectypes.DriveID(c)
