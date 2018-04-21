import os
import unittest
import types

from pykit import net
from pykit import zkutil


class TestZKutil(unittest.TestCase):

    def test_lock_data(self):

        k = zkutil.lock_data('a')
        elts = k.split('-')

        self.assertEqual(3, len(elts))

        self.assertEqual('a', elts[0])
        self.assertTrue(net.is_ip4(elts[1]))
        self.assertEqual(os.getpid(), int(elts[2]))

    def test_parse_lock_data(self):

        cases = (
                ('', ('', None, None)),
                ('-', ('', '', None)),
                ('--', ('', '', None)),
                ('1-', ('1', '', None)),
                ('1-a', ('1', 'a', None)),
                ('1-a-x', ('1', 'a', None)),
                ('1-a-1', ('1', 'a', 1)),
        )

        for inp, expected in cases:

            rst = zkutil.parse_lock_data(inp)

            self.assertTrue(
                set(['node_id', 'ip', 'process_id']) == set(rst.keys()))
            self.assertEqual(
                expected, (rst['node_id'], rst['ip'], rst['process_id']))

    def test_make_digest(self):

        cases = (
                ('aa:', 'E/ZoYMT80fFT7vhICWyvMdWNt7o='),
                ('username:password', '+Ir5sN1lGJEEs8xBZhZXKvjLJ7c=')
        )

        for inp, expected in cases:
            rst = zkutil.make_digest(inp)
            self.assertEqual(expected, rst)

    def test_make_acl_entry(self):

        def iter_perms():
            for c in 'cdrwa':
                yield c

        username = 'zookeeper_user'
        password = 'MT80fFT7vh'
        perm_cases = (
            '',
            'rw',
            'cdrwa',
            [],
            ['c'],
            ['c', 'r', 'r'],
            (),
            ('c',),
            ('c', 'r', 'w'),
            iter_perms(),
        )

        for inp in perm_cases:

            if isinstance(inp, types.GeneratorType):
                perm = 'cdrwa'
            else:
                perm = ''.join(inp)

            rst = zkutil.make_acl_entry(username, password, inp)

            rst_splited = rst.split(':')
            self.assertEqual(4, len(rst_splited))
            self.assertEqual(('digest', username, perm),
                             (rst_splited[0], rst_splited[1], rst_splited[3]))

        cases = (
                ((username, password, ''),
                 'digest:zookeeper_user:Ds8aM7UNwfAlTN3IRdkBoCno9FM=:'),
                (('aabb', 'abc123', 'cdrwa'),
                 'digest:aabb:t9MeAsoEPfdQEQjqbWtw8EHD9T0=:cdrwa')
        )

        for inp, expected in cases:
            rst = zkutil.make_acl_entry(inp[0], inp[1], inp[2])
            self.assertEqual(expected, rst)

        invalid_perm_cases = (
            'abc',
            ['cde'],
            ['a', 'v'],
            ('rw',),
            ('a', 'b', 'c'),
        )

        for inp in invalid_perm_cases:

            with self.assertRaises(zkutil.PermTypeError):
                zkutil.make_acl_entry(username, password, inp)
