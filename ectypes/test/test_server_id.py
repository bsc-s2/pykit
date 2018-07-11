#!/usr/bin/env python2
# coding: utf-8

import re
import uuid
import unittest

from pykit import ectypes
from pykit import proc
from pykit import ututil

dd = ututil.dd


class TestServerID(unittest.TestCase):

    def test_make_server_id(self):
        server_id = str(ectypes.ServerID.local_server_id())
        self.assertEqual(12, len(server_id))
        self.assertRegexpMatches(server_id, "^[0-9a-f]{12}$")
        out = proc.shell_script('ifconfig')
        self.assertIn(re.sub('(.{2})', r':\1', server_id)[1:], str(out))

    def test_validate_server_id(self):
        invalid_cases = (
            (),
            [],
            {},
            'foo',
            123,

            'aabbccddeef,'
            'aabbccddeef('
            'aabbccddeef?'
            'aabbccddeef&'
            'aabbccddEEff'
            'aabbccddeeffgg'
            'aabbccddeegg'
        )

        for c in invalid_cases:
            self.assertRaises(ValueError, ectypes.ServerID, c)

        cases = (
            '112233aabbcc',
            'aa112233bbcc',
            '112233445566',
            'aabbccddeeff',
        )

        for c in cases:
            ectypes.ServerID(c)


def test_server_id_to_str(self):
        sid = ectypes.ServerID.local_server_id()
        self.assertIsInstance(sid, ectypes.ServerID)
        self.assertEqual('%012x' % uuid.getnode(), str(sid))
        self.assertEqual('%012x' % uuid.getnode(), sid)
