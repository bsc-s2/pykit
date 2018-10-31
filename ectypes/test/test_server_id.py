#!/usr/bin/env python2
# coding: utf-8

import re
import uuid
import unittest

from pykit import ectypes
from pykit import proc
from pykit import ututil
import json

dd = ututil.dd

_idcid = 'idc123'


class TestServerID(unittest.TestCase):

    def test_make_server_id(self):

        server_id = str(ectypes.ServerID.local_server_id(_idcid))

        self.assertEqual(18, len(server_id))
        self.assertRegexpMatches(server_id, "^.{6}[0-9a-f]{12}$")
        out = proc.shell_script('ifconfig')
        self.assertIn(re.sub('(.{2})', r':\1', server_id[6:])[1:], str(out))

    def test_validate_server_id(self):
        invalid_cases = (
            ((),),
            ([],),
            ({},),
            ('foo',),
            (123,),
            (_idcid, 'aabbccddeef,',),
            (_idcid, 'aabbccddeef(',),
            (_idcid, 'aabbccddeef?',),
            (_idcid, 'aabbccddeef&',),
            (_idcid, 'aabbccddEEff',),
            (_idcid, 'aabbccddeeffgg',),
            (_idcid, 'aabbccddeegg',),

            ("12345", 'aabbccddeeff',),
            ("1234567", 'aabbccddeeff',),
        )

        for c in invalid_cases:
            self.assertRaises(ValueError, ectypes.ServerID, *c)

        cases = (
            '112233aabbcc',
            'aa112233bbcc',
            '112233445566',
            'aabbccddeeff',
        )

        for c in cases:
            sid = ectypes.ServerID(_idcid, c)
            self.assertEqual(_idcid + c, sid)

            sid = ectypes.ServerID(_idcid + c)
            self.assertEqual(_idcid + c, sid)

    def test_server_id_self(self):
        sid = ectypes.ServerID('idc000' '112233aabbcc')
        self.assertIs(sid, sid.server_id)

    def test_server_id_to_str(self):

        sid = ectypes.ServerID.local_server_id(_idcid)
        expected = _idcid + ('%012x' % uuid.getnode())

        self.assertIsInstance(sid, ectypes.ServerID)
        self.assertEqual(expected, sid)
        self.assertEqual(expected, str(sid))
        self.assertEqual(repr(expected), repr(sid))
        self.assertEqual(json.dumps(expected), json.dumps(sid))
