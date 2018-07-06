#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import ututil
from pykit.ectypes import ReplicationConfig

dd = ututil.dd


class TestReplicationConfig(unittest.TestCase):

    def test_init_lack_arg(self):

        lack_arg_cases = (
            dict(in_idc=[],     cross_idc=[1, 2]),
            dict(in_idc=[1],    cross_idc=[1, 2]),
            dict(in_idc=[1, 2], cross_idc=[]),
            dict(in_idc=[1, 2], cross_idc=[1, ]),
        )

        for arg in lack_arg_cases:
            dd(arg)
            self.assertRaises(IndexError, ReplicationConfig, arg)

    def test_init(self):

        e = ReplicationConfig(in_idc=[2, 3],
                              cross_idc=[3, 4],
                              ec_policy='xx',
                              data_replica=5)

        self.assertEqual({'in_idc': (2, 3),
                          'cross_idc': (3, 4),
                          'ec_policy': 'xx',
                          "data_replica": 5}, e)

        self.assertRaises(ValueError, ReplicationConfig,
                          in_idc=[1, 1], cross_idc=[1, 1], data_replica=0)

    def test_init_default(self):

        e = ReplicationConfig(in_idc=[2, 3],
                              cross_idc=[3, 4])

        self.assertEqual({'in_idc': (2, 3),
                          'cross_idc': (3, 4),
                          'ec_policy': 'lrc',
                          "data_replica": 1}, e)
