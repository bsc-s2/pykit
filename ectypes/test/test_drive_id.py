#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import ectypes
from pykit import ututil
from pykit.ectypes import DriveID

dd = ututil.dd

_idcid = 'idc123'

class TestDriveID(unittest.TestCase):

    def test_drive_id(self):
        cases = (
            (_idcid + '112233445566', 1),
            (_idcid + '112233445566', 10),
            (_idcid + '112233445566', 100),
            (_idcid + '112233445566', 999),

            (_idcid + 'aabbccddeeff', 1),
            (_idcid + 'aabbccddeeff', 10),
            (_idcid + 'aabbccddeeff', 100),
            (_idcid + 'aabbccddeeff', 999),

            (_idcid + '1122ccddeeff', 1),
            (_idcid + '1122ccddeeff', 10),
            (_idcid + '1122ccddeeff', 100),
            (_idcid + '1122ccddeeff', 999),
        )

        for sid, mp_idx in cases:
            drive_id = DriveID(sid, mp_idx)
            self.assertEqual(sid, drive_id.server_id)
            self.assertEqual('%03d' % mp_idx, drive_id.mountpoint_index)
            self.assertEqual(mp_idx, int(drive_id.mountpoint_index))
            self.assertEqual('%s0%03d' % (sid[:18], mp_idx % 1000), drive_id)

            drvid = DriveID(drive_id)
            self.assertEqual(sid, drvid.server_id)
            self.assertEqual(drvid, DriveID(drvid))

    def test_drive_id_server_id(self):

        for drive_id in (DriveID('idc000112233445566', 1),
                         DriveID('idc0001122334455660001')):

            dd(drive_id)

            self.assertIsInstance(drive_id.server_id, str)
            self.assertEqual('idc000112233445566', drive_id.server_id)
            self.assertEqual('idc0001122334455660001', str(drive_id))

    def test_validate_drive_id(self):
        invalid_cases = (
            (),
            [],
            {},
            'foo',
            123,
            'idc000' 'aabbccddeeff*001',
            'idc000' 'aabbccddeeff000a',
            'idc000' '*&bbccddeeff0001',
            'idc000' 'AAbbccddeeff0001',
            'idc000' 'AAbbccddeeff0xxx',
        )

        for c in invalid_cases:
            dd(c)
            self.assertRaises(ValueError, ectypes.DriveID, c)

        cases = (
            'idc000' 'aabbccddeeff0001',
            'idc000' 'aabbccddeeff0100',
            'idc000' 'aabbccddeeff0999',
            'idc000' '11bbccddeeff0999',
            'idc000' '11bb33ddeeff0999',
        )

        for c in cases:
            ectypes.DriveID(c)
