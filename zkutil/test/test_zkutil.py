import os
import unittest

from pykit import net
from pykit import ututil
from pykit import zkutil

dd = ututil.dd


class TestZKutil(unittest.TestCase):

    def test_lock_data(self):

        k = zkutil.lock_data('a')
        dd(k)
        elts = k.split('-')

        self.assertEqual(4, len(elts))

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

            self.assertEqual(set(['node_id', 'ip', 'process_id', 'counter']),
                             set(rst.keys()))

            self.assertEqual(expected,
                             (rst['node_id'], rst['ip'], rst['process_id']))

    def test_make_digest(self):

        cases = (
                ('aa:', 'E/ZoYMT80fFT7vhICWyvMdWNt7o='),
                ('username:password', '+Ir5sN1lGJEEs8xBZhZXKvjLJ7c=')
        )

        for inp, expected in cases:
            rst = zkutil.make_digest(inp)
            self.assertEqual(expected, rst)

    def test_make_acl_entry(self):

        username = 'zookeeper_user'
        password = 'MT80fFT7vh'
        perm_cases = [
            '',
            'rw',
            'cdrwa',
            [],
            ['c'],
            ['c', 'r', 'r'],
            (),
            ('c',),
            ('c', 'r', 'w'),
            iter('cdrwa'),
        ]

        for inp in perm_cases:

            if isinstance(inp, type(iter(''))):
                perm = 'cdrwa'
            else:
                perm = ''.join(inp)

            dd('inp=', inp)
            dd('perm=', perm)
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

    def test_permission_convert(self):

        perm_cases = (
            ('',              [], ''),
            ('rw',            ['read', 'write'], 'rw'),
            ('cdrwa',         ['create', 'delete', 'read', 'write', 'admin'], 'cdrwa'),
            ([],              [], ''),
            (['c'],           ['create'], 'c'),
            (['c', 'r', 'r'], ['create', 'read', 'read'], 'crr'),
            ((),              [], ''),
            (('c',),          ['create'], 'c'),
            (('c', 'r', 'w'), ['create', 'read', 'write'], 'crw'),
            (iter('cdrwa'),   ['create', 'delete', 'read', 'write', 'admin'], 'cdrwa'),
        )

        for inp, lng, short in perm_cases:

            rst = zkutil.perm_to_long(inp)
            self.assertEqual(lng, rst)

            rst = zkutil.perm_to_short(lng)
            self.assertEqual(short, rst)

        # invalid short format

        invalid_short = (
            'abc',
            ['cde'],
            ['a', 'v'],
            ('rw',),
            ('a', 'b', 'c'),
        )

        for inp in invalid_short:
            self.assertRaises(zkutil.PermTypeError, zkutil.perm_to_long, inp)

        # invalid long format

        invalid_long = (
            'abc',
            ['foo'],
        )

        for inp in invalid_long:
            self.assertRaises(zkutil.PermTypeError, zkutil.perm_to_short, inp)
