import os
import time
import unittest
import uuid

from kazoo import security
from kazoo.client import KazooClient
from kazoo.exceptions import ConnectionClosedError
from kazoo.exceptions import NoNodeError

from pykit import config
from pykit import net
from pykit import threadutil
from pykit import utdocker
from pykit import ututil
from pykit import zkutil

dd = ututil.dd

zk_tag = 'daocloud.io/zookeeper:3.4.10'
zk_name = 'zk_test'


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

            self.assertEqual(set(['node_id', 'ip', 'process_id', 'uuid', 'txid']),
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
            ('cdrwa',         ['create', 'delete',
                               'read', 'write', 'admin'], 'cdrwa'),
            ([],              [], ''),
            (['c'],           ['create'], 'c'),
            (['c', 'r', 'r'], ['create', 'read', 'read'], 'crr'),
            ((),              [], ''),
            (('c',),          ['create'], 'c'),
            (('c', 'r', 'w'), ['create', 'read', 'write'], 'crw'),
            (iter('cdrwa'),   ['create', 'delete',
                               'read', 'write', 'admin'], 'cdrwa'),
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


class TestZKinit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        utdocker.pull_image(zk_tag)

    def setUp(self):

        utdocker.create_network()

        utdocker.start_container(
            zk_name,
            zk_tag,
            port_bindings={2181: 2181}
        )

        dd('start zk-test in docker')

    def tearDown(self):

        utdocker.stop_container(zk_name)
        utdocker.remove_container(zk_name)

        dd('remove_container: ' + zk_name)

    def test_init_hierarchy(self):

        auth = ('digest', 'aa', 'pw_aa')
        hosts = '127.0.0.1:2181'
        users = {'aa': 'pw_aa', 'bb': 'pw_bb', 'cc': 'pw_cc'}
        hierarchy = {
            'node1':
            {
                '__val__': 'node1_val',
                '__acl__': {'aa': 'cdrwa', 'bb': 'rw'},
                'node11':
                {
                    '__val__': 'node11_val',
                    '__acl__': {'aa': 'cdrwa', 'cc': 'r'},
                },
                'node12':
                {
                    '__val__': 'node12_val',
                    'node121': {'__val__': 'node121_val'}
                },
                'node13':
                {
                    '__acl__': {'aa': 'cdrwa'}
                }
            },
            'node2':
            {
                '__val__': 'node2_val',
                'node21': {'__val__': 'node21_val'},
                'node22': {'__acl__': {'aa': 'rwa'}}
            },
            'node3':
            {
                '__acl__': {'aa': 'carw', 'cc': 'r'},
                'node31': {'node311': {'node3111': {}, 'node3112': {}}}
            }
        }

        zkutil.init_hierarchy(hosts, hierarchy, users, auth)

        zkcli = KazooClient(hosts)
        zkcli.start()
        zkcli.add_auth('digest', 'aa:pw_aa')

        expected_nodes = (
            ('/node1', '"node1_val"', [('digest', 'aa', 'cdrwa'),
                                       ('digest', 'bb', 'rw')], set(['node11', 'node12', 'node13'])),
            ('/node1/node11', '"node11_val"',
             [('digest', 'aa', 'cdrwa'), ('digest', 'cc', 'r')], set([])),
            ('/node1/node12', '"node12_val"',
             [('digest', 'aa', 'cdrwa'), ('digest', 'bb', 'rw')], set(['node121'])),
            ('/node1/node12/node121', '"node121_val"',
             [('digest', 'aa', 'cdrwa'), ('digest', 'bb', 'rw')], set([])),
            ('/node1/node13', '{}', [('digest', 'aa', 'cdrwa')], set([])),

            ('/node2', '"node2_val"',
             [('world', 'anyone', 'cdrwa')], set(['node21', 'node22'])),
            ('/node2/node21', '"node21_val"',
             [('world', 'anyone', 'cdrwa')],  set([])),
            ('/node2/node22', '{}', [('digest', 'aa', 'rwa')],  set([])),

            ('/node3', '{}', [('digest', 'aa', 'rwca'),
                              ('digest', 'cc', 'r')], set(['node31'])),
            ('/node3/node31', '{}', [('digest', 'aa', 'rwca'),
                                     ('digest', 'cc', 'r')],  set(['node311'])),
            ('/node3/node31/node311', '{}',
             [('digest', 'aa', 'rwca'), ('digest', 'cc', 'r')], set(['node3111', 'node3112'])),
            ('/node3/node31/node311/node3111', '{}',
             [('digest', 'aa', 'rwca'), ('digest', 'cc', 'r')], set([])),
            ('/node3/node31/node311/node3112', '{}',
             [('digest', 'aa', 'rwca'), ('digest', 'cc', 'r')], set([])),
        )

        for node, val, acl, children in expected_nodes:

            actual_acl = zkutil.parse_kazoo_acl(zkcli.get_acls(node)[0])
            self.assertEqual(val, zkcli.get(node)[0])
            self.assertEqual(acl, actual_acl)
            self.assertEqual(children, set(zkcli.get_children(node)))

        zkcli.stop()


class TestWait(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        utdocker.pull_image(zk_tag)

    def setUp(self):

        utdocker.create_network()
        utdocker.start_container(
            zk_name,
            zk_tag,
            env={
                "ZOO_MY_ID": 1,
                "ZOO_SERVERS": "server.1=0.0.0.0:2888:3888",
            },
            port_bindings={2181: 2181}
        )

        self.zk = KazooClient('127.0.0.1:2181')
        self.zk.start()

        dd('start zk-test in docker')

    def tearDown(self):

        self.zk.stop()
        utdocker.remove_container(zk_name)

    def test_wait_absent(self):

        for wait_time in (
                -1,
                0.0,
                0.1,
                1,
        ):

            dd('no node wait:', wait_time)

            with ututil.Timer() as t:
                zkutil.wait_absent(self.zk, 'a', wait_time)
                self.assertAlmostEqual(0, t.spent(), delta=0.2)

    def test_wait_absent_no_timeout(self):

        def _del():
            time.sleep(1)
            self.zk.delete('a')

        for kwargs in (
            {},
                {'timeout': None},
        ):

            self.zk.create('a')
            th = threadutil.start_daemon(target=_del)

            with ututil.Timer() as t:
                zkutil.wait_absent(self.zk, 'a', **kwargs)
                self.assertAlmostEqual(1, t.spent(), delta=0.1)

            th.join()

    def test_wait_absent_timeout(self):

        self.zk.create('a')

        for wait_time in (
                -1,
                0.0,
                0.1,
                1,
        ):
            dd('node present wait:', wait_time)
            expected = max([0, wait_time])

            with ututil.Timer() as t:
                self.assertRaises(zkutil.ZKWaitTimeout,
                                  zkutil.wait_absent,
                                  self.zk, 'a', timeout=wait_time)
                self.assertAlmostEqual(expected, t.spent(), delta=0.2)

        self.zk.delete('a')

    def test_wait_absent_delete_node(self):

        delete_after = 0.2

        for wait_time in (
                0.5,
                1,
        ):
            dd('node present wait:', wait_time)

            self.zk.create('a')

            def _del():
                time.sleep(delete_after)
                self.zk.delete('a')

            th = threadutil.start_daemon(target=_del)
            with ututil.Timer() as t:
                zkutil.wait_absent(self.zk, 'a', wait_time)
                self.assertAlmostEqual(delete_after, t.spent(), delta=0.1)

            th.join()

    def test_wait_absent_change_node(self):

        self.zk.create('a')

        change_after = 0.2

        for wait_time in (
                0.5,
                1,
        ):
            dd('node present wait:', wait_time)
            expected = max([0, wait_time])

            def _change():
                time.sleep(change_after)
                self.zk.set('a', 'bbb')

            th = threadutil.start_daemon(target=_change)
            with ututil.Timer() as t:
                self.assertRaises(zkutil.ZKWaitTimeout,
                                  zkutil.wait_absent,
                                  self.zk, 'a', timeout=wait_time)
                self.assertAlmostEqual(expected, t.spent(), delta=0.1)

            th.join()

        self.zk.delete('a')

    def test_wait_absent_connection_lost(self):

        self.zk.create('a')

        def _close():
            time.sleep(.3)
            self.zk.stop()

        th = threadutil.start_daemon(target=_close)

        with ututil.Timer() as t:
            self.assertRaises(ConnectionClosedError,
                              zkutil.wait_absent,
                              self.zk, 'a')
            self.assertAlmostEqual(.3, t.spent(), delta=0.1)

        th.join()

    def test_get_next_no_version(self):

        cases = (
            -1,
            0.0,
            0.1,
            1,
        )

        for timeout in cases:

            self.zk.create('a', 'a-val')

            with ututil.Timer() as t:
                zkutil.get_next(self.zk, 'a', timeout=timeout, version=-1)
                self.assertAlmostEqual(0, t.spent(), delta=0.2)

            with ututil.Timer() as t:
                zkutil.get_next(self.zk, 'a', timeout=timeout)
                self.assertAlmostEqual(0, t.spent(), delta=0.2)

            self.zk.delete('a')

    def test_get_next_timeout(self):

        cases = (
            -1,
            0.0,
            0.2,
            1,
        )

        for timeout in cases:

            expected = max([timeout, 0])
            self.zk.create('a', 'a-val')

            with ututil.Timer() as t:
                self.assertRaises(zkutil.ZKWaitTimeout,
                                  zkutil.get_next,
                                  self.zk, 'a', timeout=timeout, version=0)
                self.assertAlmostEqual(expected, t.spent(), delta=0.2)

            self.zk.delete('a')

    def test_get_next_changed(self):

        cases = (
            0.4,
            1,
        )

        def _set_a():
            self.zk.set('a', 'changed')

        for timeout in cases:

            self.zk.create('a', 'a-val')
            th = threadutil.start_daemon(target=_set_a, after=0.3)

            with ututil.Timer() as t:
                val, zstat = zkutil.get_next(self.zk, 'a', timeout=timeout, version=0)
                self.assertAlmostEqual(0.3, t.spent(), delta=0.2)
                self.assertEqual('changed', val)
                self.assertEqual(1, zstat.version)

            th.join()
            self.zk.delete('a')

    def test_get_next_changed_but_unsatisfied(self):

        cases = (
            0.4,
            1,
        )

        def _set_a():
            self.zk.set('a', 'changed')

        for timeout in cases:

            self.zk.create('a', 'a-val')
            th = threadutil.start_daemon(target=_set_a, after=0.3)

            with ututil.Timer() as t:
                self.assertRaises(zkutil.ZKWaitTimeout,
                                  zkutil.get_next,
                                  self.zk, 'a', timeout=timeout, version=5)
                self.assertAlmostEqual(timeout, t.spent(), delta=0.2)

            th.join()
            self.zk.delete('a')

    def test_get_next_deleted(self):

        cases = (
            0.4,
            1,
        )

        def _del_a():
            self.zk.delete('a')

        for timeout in cases:

            self.zk.create('a', 'a-val')
            th = threadutil.start_daemon(target=_del_a, after=0.3)

            with ututil.Timer() as t:
                self.assertRaises(NoNodeError,
                                  zkutil.get_next,
                                  self.zk, 'a', timeout=timeout, version=0)
                self.assertAlmostEqual(0.3, t.spent(), delta=0.2)

            th.join()

    def test_get_next_conn_lost(self):

        self.zk.create('a', 'a-val')
        th = threadutil.start_daemon(target=self.zk.stop, after=0.3)

        with ututil.Timer() as t:
            self.assertRaises(ConnectionClosedError,
                              zkutil.get_next,
                              self.zk, 'a', timeout=1, version=0)
            self.assertAlmostEqual(0.3, t.spent(), delta=0.2)

        th.join()
