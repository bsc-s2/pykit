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


class TestIDCID(unittest.TestCase):

    def test_validate_idc_id(self):
        invalid_cases = (
            (),
            [],
            {},
            'foo',
            123,

            '12345',
            '1234567',
        )

        for c in invalid_cases:
            self.assertRaises(ValueError, ectypes.IDCID, c)

        cases = (
            '123456',
            '!@#$%^',
            'abcdef',
            'ABCDEF',
        )

        for c in cases:
            ectypes.IDCID(c)


    def test_idc_id_to_str(self):

        sid = ectypes.IDCID('123456')

        self.assertIsInstance(sid, ectypes.IDCID)
        self.assertEqual('123456', str(sid))
        self.assertEqual('123456', sid)
        self.assertEqual("'123456'", repr(sid))
        self.assertEqual('"123456"', json.dumps(sid))
