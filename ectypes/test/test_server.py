#!/usr/bin/env python2
# coding: utf-8

import mock
import socket
import unittest

import psutil

from pykit import ectypes
from pykit import ututil

dd = ututil.dd


class TestServer(unittest.TestCase):

    @mock.patch("pykit.ectypes.server._make_mountpoints_info")
    def test_serverrec(self, mock_mnt):
        cases = (
            (
                'idc000',
                'center',
                {'role1': 1},
                {"/foo": {"fs": "vfs", "capacity": 100}},
                {'foo': 1}
            ),

            (
                'idc001',
                'xx',
                {'role1': 1, 'role2': 1},
                {"/foo": {"fs": "vfs", "capacity": 100}, "/bar/d/010": {"fs": "vfs", "capacity": 200}},
                {'foo': 1, 'bar': 2}
            ),

            (
                'idc002',
                'yy',
                {'role1': 1, 'role2': 1, 'role3': 1},
                {},
                {'foo': 1}
            ),

            (
                'idc003',
                'zz',
                {'role1': 1, 'role4': 4},
                {"/bar/d/020": {"fs": "vfs", "capacity": 1000}, "/bar/d/010": {"fs": "vfs", "capacity": 200}},
                {'foo': 1, 'bar': 2, 'foobar': 3}
            ),
        )

        for idc, idc_type, roles, mnt_info, argkv in cases:
            mock_mnt.return_value = mnt_info
            serverrec = ectypes.make_serverrec('idc000aabbccddeeff', idc, idc_type, roles, '/bar', **argkv)

            dd('serverrec:' + repr(serverrec))

            self.assertIn('server_id', serverrec)
            self.assertIn('pub_ips', serverrec)
            self.assertIn('inn_ips', serverrec)
            self.assertIn('memory', serverrec)

            self.assertEqual('idc000aabbccddeeff', serverrec['server_id'])

            self.assertIn('count', serverrec['cpu'])
            if hasattr(psutil, 'cpu_freq'):
                self.assertIn('frequency', serverrec['cpu'])

            self.assertEqual(serverrec['mountpoints'], mnt_info)

            idx = 0
            for mp, info in mnt_info.items():
                if not mp.startswith('/bar'):
                    continue

                mp_idx = int(mp.split('/')[-1])
                idx = idx if idx > mp_idx else mp_idx
                self.assertEqual(serverrec['allocated_drive'][mp], {'status': 'normal'})

            self.assertEqual(idx + 1, serverrec['next_mount_index'])
            dd("next_mount_index:", serverrec['next_mount_index'])

            self.assertEqual(socket.gethostname(), serverrec['hostname'])
            self.assertEqual(idc, serverrec['idc'])
            self.assertEqual(idc_type, serverrec['idc_type'])
            self.assertEqual(roles, serverrec['roles'])

            for k, v in argkv.items():
                self.assertEqual(v, serverrec[k])

            serverrec_str = ectypes.get_serverrec_str(serverrec)
            dd('serverrec_str:' + repr(serverrec_str))

            exp_str = ('server_id: {sid}; idc: {idc}; idc_type: {idct}; roles: {r};'
                       ' mountpoints_count: {mp_cnt}; allocated_drive_count: {ad_cnt}').format(
                sid=serverrec['server_id'], idc=idc, idct=idc_type,
                r=roles, mp_cnt=len(serverrec['mountpoints']),
                ad_cnt=len(serverrec['allocated_drive']))

            self.assertEqual(exp_str, serverrec_str)

    def test_validate_idc(self):
        invalid_cases = (
            {},
            (),
            [],
            'l1',
            '*l1.l2',
            '&l1.l2.l3',

            '.l&&',
            '.l1.l*',
        )

        for c in invalid_cases:
            self.assertFalse(ectypes.validate_idc(c))

        cases = (
            '',
            '.',
            '.l1',
            '.l1.l2',
            '.l1.l2.l3',
            '.l1.l2.l3.l4',

            '.L1',
            '.L1.L2',
            '.L1.L2.L3',
            '.L1.L2.L3.L4',
        )

        for c in cases:
            self.assertTrue(ectypes.validate_idc(c))

    def test_idc_distance(self):
        cases = (
            ('', '', 0),
            ('.', '.', 0),
            ('.wt', '.wt', 0),
            ('.wt.TJ', '.wt.TJ', 0),
            ('.wt.TJ.xx', '.wt.TJ.yy', 4),
            ('.wt.XD', '.wt.TJ', 8),
            ('.dx.GZ', '.wt.TJ', 16),
            ('.dx', '.wt', 16),
            ('.dx.GZ', '.dx', 8),
        )

        for n1, n2, dis in cases:
            self.assertEqual(dis, ectypes.idc_distance(n1, n2))
