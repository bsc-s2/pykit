import os
import unittest
import uuid

from kazoo import security

from pykit import config
from pykit import net
from pykit import ututil
from pykit import zkutil

dd = ututil.dd


class TestZKutil(unittest.TestCase):

    def test_lock_id(self):

        k = zkutil.lock_id('a')
        dd(k)
        elts = k.split('-')

        self.assertEqual(4, len(elts))

        self.assertEqual('a', elts[0])
        self.assertTrue(net.is_ip4(elts[1]))
        self.assertEqual(os.getpid(), int(elts[2]))

    def test_lock_id_default(self):

        expected = '%012x' % uuid.getnode()

        k = zkutil.lock_id()
        dd(config)
        dd(k)
        self.assertEqual(expected, k.split('-')[0])

        k = zkutil.lock_id(node_id=None)
        dd(k)
        self.assertEqual(expected, k.split('-')[0])

        config.zk_node_id = 'a'
        k = zkutil.lock_id(node_id=None)
        dd(k)
        self.assertEqual('a', k.split('-')[0])

    def test_parse_lock_id(self):

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

            rst = zkutil.parse_lock_id(inp)

            self.assertEqual(set(['node_id', 'ip', 'process_id', 'counter', 'txid']),
                             set(rst.keys()))

            self.assertEqual(expected,
                             (rst['node_id'], rst['ip'], rst['process_id']))

    def test_parse_lock_id_with_txid(self):

        rst = zkutil.parse_lock_id('txid:123-a-b-x')
        self.assertEqual('txid:123', rst['node_id'])
        self.assertEqual('123', rst['txid'])

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

    def test_permission_convert_case(self):

        self.assertEqual(['CREATE', 'DELETE', 'READ', 'WRITE', 'ADMIN'],
                         zkutil.perm_to_long('cdrwa', lower=False))

        self.assertEqual(['CREATE', 'DELETE', 'READ', 'WRITE', 'ADMIN'],
                         zkutil.perm_to_long('CDRWA', lower=False))

        self.assertEqual(['create', 'delete', 'read', 'write', 'admin'],
                         zkutil.perm_to_long('CDRWA'))

        self.assertEqual('CDRWA',
                         zkutil.perm_to_short(['create', 'delete', 'read', 'write', 'admin'],
                                              lower=False))

        self.assertEqual('CDRWA',
                         zkutil.perm_to_short(['CREATE', 'DELETE', 'READ', 'WRITE', 'ADMIN'],
                                              lower=False))
        self.assertEqual('cdrwa',
                         zkutil.perm_to_short(['CREATE', 'DELETE', 'READ', 'WRITE', 'ADMIN']))

    def test_make_kazoo_digest_acl(self):

        inp = (('foo', 'bar', 'cd'),
               ('xp', '123', 'cdrwa'))

        dd(inp)

        rst = zkutil.make_kazoo_digest_acl(inp)
        dd(rst)

        self.assertEqual(2, len(rst))

        ac = rst[0]
        self.assertEqual('digest', ac.id.scheme)
        self.assertEqual('foo', ac.id.id.split(':')[0])
        self.assertEqual(set(['CREATE', 'DELETE']), set(ac.acl_list))

        ac = rst[1]
        self.assertEqual('digest', ac.id.scheme)
        self.assertEqual('xp', ac.id.id.split(':')[0])
        self.assertEqual(set(['ALL']), set(ac.acl_list))

        self.assertIsNone(zkutil.make_kazoo_digest_acl(None))

    def test_parse_kazoo_acl(self):

        inp = (security.make_acl('world', 'anyone', all=True),
               security.make_digest_acl('foo', 'bar', create=True, read=True),
               security.make_digest_acl('xp', '123', all=True),
               )
        expected = (('world', 'anyone', 'cdrwa'),
                    ('digest', 'foo', 'rc'),
                    ('digest', 'xp', 'cdrwa'))

        dd(inp)

        rst = zkutil.parse_kazoo_acl(inp)
        dd(rst)

        self.assertEqual(expected, tuple(rst))

    def test_is_backward_locking(self):

        cases = (
            ([],         'a', False, None),
            (['a'],      'a', False, AssertionError),
            (['a', 'c'], 'a', True,  AssertionError),
            (['a', 'c'], 'c', True,  AssertionError),
            (['a', 'c'], '',  True,  None),
            (['a', 'c'], 'b', True,  None),
            (['a', 'c'], 'd', False, None),
        )

        for locked, key, expected, err in cases:

            if err is None:
                rst = zkutil.is_backward_locking(locked, key)
                self.assertEqual(expected, rst)
            else:
                self.assertRaises(err, zkutil.is_backward_locking, locked, key)
