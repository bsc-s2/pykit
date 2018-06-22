#!/usr/bin/env python2
# coding: utf-8

import re
import socket
import unittest
import uuid

import psutil

from pykit import cluster
from pykit import proc
from pykit import ututil

dd = ututil.dd


class TestClusterServer(unittest.TestCase):

    def test_make_server_id(self):
        server_id = str(cluster.ServerID.local_server_id())
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
            self.assertFalse(cluster.ServerID.validate(c))

        cases = (
            '112233aabbcc',
            'aa112233bbcc',
            '112233445566',
            'aabbccddeeff',
        )

        for c in cases:
            self.assertTrue(cluster.ServerID.validate(c))

    def test_server_id_to_str(self):
        sid = cluster.ServerID.local_server_id()
        self.assertIsInstance(sid, cluster.ServerID)
        self.assertEqual('%012x' % uuid.getnode(), str(sid))
        self.assertEqual('%012x' % uuid.getnode(), sid)

    def test_serverrec(self):
        cases = (
            ('.l1', 'center', {'role1': 1}, {'foo': 1}),
            ('.l1.l2', 'xx', {'role1': 1, 'role2': 1}, {'foo': 1, 'bar': 2}),
            ('.l1.l2.l3', 'yy', {'role1': 1, 'role2': 1, 'role3': 1}, {'foo': 1}),
            ('.l1.l2.l3.l4', 'zz', {'role1': 1, 'role4': 4}, {'foo': 1, 'bar': 2, 'foobar': 3}),
        )

        for idc, idc_type, roles, argkv in cases:
            serverrec = cluster.make_serverrec(idc, idc_type, roles, '/s2', **argkv)

            dd('serverrec:' + repr(serverrec))

            self.assertIn('server_id', serverrec)
            self.assertIn('pub_ips', serverrec)
            self.assertIn('inn_ips', serverrec)
            self.assertIn('memory', serverrec)

            self.assertIn('count', serverrec['cpu'])
            if hasattr(psutil, 'cpu_freq'):
                self.assertIn('frequency', serverrec['cpu'])

            self.assertIn('mountpoints', serverrec)
            self.assertEqual(1, serverrec['next_mount_index'])
            self.assertIn('allocated_drive', serverrec)

            for k, v in serverrec['allocated_drive'].items():
                self.assertIn('/s2', k)
                self.assertEqual({'status': 'normal'}, v)

            self.assertEqual(socket.gethostname(), serverrec['hostname'])
            self.assertEqual(idc, serverrec['idc'])
            self.assertEqual(idc_type, serverrec['idc_type'])
            self.assertEqual(roles, serverrec['roles'])

            for k, v in argkv.items():
                self.assertEqual(v, serverrec[k])

            serverrec_str = cluster.get_serverrec_str(serverrec)
            dd('serverrec_str:' + repr(serverrec_str))

            exp_str = ('server_id: {sid}; idc: {idc}; idc_type: {idct}; roles: {r};'
                       ' mountpoints_count: {mp_cnt}; allocated_drive_count: {ad_cnt}').format(
                sid=serverrec['server_id'], idc=idc, idct=idc_type,
                r=roles, mp_cnt=len(serverrec['mountpoints']),
                ad_cnt=len(serverrec['allocated_drive']))

            self.assertEqual(exp_str, serverrec_str)

    def test_drive_id(self):
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
            drive_id = str(cluster.DriveID(sid, mp_idx))
            self.assertEqual('%s0%03d' % (sid[:12], mp_idx % 1000),
                             drive_id)

            self.assertEqual(sid, cluster.DriveID.parse(drive_id).server_id)
            self.assertEqual(mp_idx, cluster.DriveID.parse(drive_id).mountpoint_index)

    def test_drive_id_server_id(self):

        for drive_id in (cluster.DriveID('112233445566', 1),
                         cluster.DriveID.parse('1122334455660001')):

            dd(drive_id)

            self.assertIsInstance(drive_id.server_id, str)
            self.assertEqual('112233445566', drive_id.server_id)
            self.assertEqual('1122334455660001', drive_id.tostr())
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
            self.assertFalse(cluster.DriveID.validate(c))

        cases = (
            'aabbccddeeff0001',
            'aabbccddeeff0100',
            'aabbccddeeff0999',
            '11bbccddeeff0999',
            '11bb33ddeeff0999',
        )

        for c in cases:
            self.assertTrue(cluster.DriveID.validate(c))

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
            self.assertFalse(cluster.validate_idc(c))

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
            self.assertTrue(cluster.validate_idc(c))

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
            self.assertEqual(dis,
                             cluster.idc_distance(n1, n2))
