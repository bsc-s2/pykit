
import time
import unittest

from kazoo.client import KazooClient
from kazoo.exceptions import ConnectionClosedError

from pykit import config
from pykit import threadutil
from pykit import utdocker
from pykit import ututil
from pykit import zkutil

dd = ututil.dd

zk_test_name = 'zk_test'
zk_test_tag = 'daocloud.io/zookeeper:3.4.10'
zk_test_auth = ('digest', 'xp', '123')
zk_test_acl = (('xp', '123', 'cdrw'), )

# zookeeper docker env vars:
# https://hub.docker.com/_/zookeeper/
#
# Example stack.yml for zookeeper:
#
# version: '3.1'
# services:
#   zoo1:
#     image: zookeeper
#     restart: always
#     hostname: zoo1
#     ports:
#       - 2181:2181
#     environment:
#       ZOO_MY_ID: 1
#       ZOO_SERVERS: server.1=0.0.0.0:2888:3888 server.2=zoo2:2888:3888 server.3=zoo3:2888:3888
#   zoo2: ...
#   zoo3: ...
#
# ZOO_TICK_TIME          : Defaults to 2000. ZooKeeper's tickTime
# ZOO_INIT_LIMIT         : Defaults to 5. ZooKeeper's initLimit
# ZOO_SYNC_LIMIT         : Defaults to 2. ZooKeeper's syncLimit
# ZOO_MAX_CLIENT_CNXNS   : Defaults to 60. ZooKeeper's maxClientCnxns
# ZOO_STANDALONE_ENABLED : Defaults to false. Zookeeper's standaloneEnabled
# ZOO_MY_ID
# ZOO_SERVERS
#
# Where to store data
#       This image is configured with volumes at /data and /datalog to hold the Zookeeper in-memory database snapshots and the transaction log of updates to the database, respectively.


class TestZKLock(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        utdocker.pull_image(zk_test_tag)

    def setUp(self):

        config.zk_acl = zk_test_acl
        config.zk_auth = zk_test_auth

        self.counter = 0
        self.running = True

        utdocker.create_network()
        utdocker.start_container(
            zk_test_name,
            zk_test_tag,
            env={
                "ZOO_MY_ID": 1,
                "ZOO_SERVERS": "server.1=0.0.0.0:2888:3888",
            },
            port_bindings={
                2181: 2181,
            }
        )

        self.zk = KazooClient(hosts='127.0.0.1:2181')
        self.zk.start()
        scheme, name, passw = zk_test_auth
        self.zk.add_auth(scheme, name + ':' + passw)

        # create lock base dir
        acl = zkutil.make_kazoo_digest_acl(zk_test_acl)
        self.zk.create('lock/', acl=acl)

        self.lck = zkutil.ZKLock('foo_name', zkclient=self.zk)

    def tearDown(self):

        self.zk.stop()
        utdocker.remove_container(zk_test_name)

    def _on_conn_change(self, state):

        self.lsn_count += 1

    def test_bounded_listener(self):

        # ensure that adding a bounded listener(self.on_xxx) is ok

        self.lsn_count = 0

        self.zk.add_listener(self._on_conn_change)
        self.zk.add_listener(self._on_conn_change)

        self.zk.stop()

        self.assertEqual(1, self.lsn_count)

    def _loop_acquire(self, n, ident):

        zk = KazooClient(hosts='127.0.0.1:2181')
        zk.start()
        scheme, name, passw = zk_test_auth
        zk.add_auth(scheme, name + ':' + passw)

        for ii in range(n):
            l = zkutil.ZKLock('foo_name', zkclient=zk)
            with l:

                self.total += 1
                self.counter += 1

                self.assertTrue(self.counter == 1)

                time.sleep(0.01)
                self.counter -= 1

                dd("id={ident:0>2} n={ii:0>2} got and released lock: {holder}".format(
                    ident=ident,
                    ii=ii,
                    holder=l.lock_holder))

        zk.stop()

    def test_concurrent(self):

        self.running = True
        self.total = 0
        n_repeat = 40
        n_thread = 5

        ths = []
        for ii in range(n_thread):
            t = threadutil.start_daemon_thread(self._loop_acquire, args=(n_repeat, ii,))
            ths.append(t)

        for th in ths:
            th.join()

        self.running = False
        self.assertEqual(n_repeat * n_thread, self.total)

    def test_persistent(self):
        l = zkutil.ZKLock('foo_name', ephemeral=False, on_lost=lambda: True)
        try:
            with l:
                l.zkclient.stop()
        except ConnectionClosedError:
            pass

        self.assertRaises(zkutil.LockTimeout, self.lck.acquire, timeout=0.2)

    def test_timeout(self):

        l1 = zkutil.ZKLock('foo_name', on_lost=lambda: True)
        l2 = zkutil.ZKLock('foo_name', on_lost=lambda: True)

        with l1:
            with ututil.Timer() as t:
                self.assertRaises(zkutil.LockTimeout, l2.acquire, timeout=0.2)
                self.assertAlmostEqual(0.2, t.spent(), places=1)

            with ututil.Timer() as t:
                self.assertRaises(zkutil.LockTimeout, l2.acquire, timeout=-1)
                self.assertAlmostEqual(0.0, t.spent(), delta=0.01)

        try:
            l2.acquire(timeout=-1)
        except zkutil.LockTimeout:
            self.fail('timeout<0 should could acquire')

    def test_lock_holder(self):
        a = zkutil.ZKLock('foo_name', on_lost=lambda: True)
        b = zkutil.ZKLock('foo_name', on_lost=lambda: True)

        with a:
            self.assertEqual((a.identifier, 0), a.lock_holder)
            val, zstate = self.zk.get(a.lock_path)
            self.assertEqual((val, zstate.version), a.lock_holder)

            locked, holder, ver = b.try_acquire()
            self.assertFalse(locked)
            self.assertEqual((a.identifier, 0), (holder, ver))
            self.assertEqual((val, zstate.version), (holder, ver))

    def test_watch_acquire(self):

        a = zkutil.ZKLock('foo', on_lost=lambda: True)
        b = zkutil.ZKLock('foo', on_lost=lambda: True)

        # no one locked

        n = 0
        for holder, ver in a.acquire_loop():
            n += 1
        self.assertEqual(0, n, 'acquired directly')

        # watch node change

        it = b.acquire_loop()

        holder, ver = it.next()
        self.assertEqual((a.identifier, 0), (holder, ver))

        self.zk.set(a.lock_path, 'xx')
        holder, ver = it.next()
        self.assertEqual(('xx', 1), (holder, ver), 'watched node change')

        a.release()
        try:
            holder, ver = it.next()
            self.fail('should not have next yield')
        except StopIteration:
            pass

        self.assertTrue(b.is_locked())

    def test_try_lock(self):

        l1 = zkutil.ZKLock('foo_name', on_lost=lambda: True)
        l2 = zkutil.ZKLock('foo_name', on_lost=lambda: True)

        with l1:
            with ututil.Timer() as t:
                locked, holder, ver = l2.try_acquire()
                self.assertFalse(locked)
                self.assertEqual(l1.identifier, holder)
                self.assertGreaterEqual(ver, 0)

                self.assertAlmostEqual(0.0, t.spent(), delta=0.05)

        with ututil.Timer() as t:
            locked, holder, ver = l2.try_acquire()
            self.assertTrue(locked)
            self.assertEqual(l2.identifier, holder)
            self.assertEqual(ver, 0)

            self.assertAlmostEqual(0.0, t.spent(), delta=0.05)

    def test_try_release(self):

        l1 = zkutil.ZKLock('foo_name', on_lost=lambda: True)
        l2 = zkutil.ZKLock('foo_name', on_lost=lambda: True)

        released, holder, ver = l1.try_release()
        self.assertEqual((True, l1.identifier, -1), (released, holder, ver))

        with l2:
            released, holder, ver = l1.try_release()
            self.assertEqual((False, l2.identifier, 0), (released, holder, ver))

            released, holder, ver = l2.try_release()
            self.assertEqual((True, l2.identifier, 0), (released, holder, ver))

    def test_zk_lost(self):

        sess = {'acquired': True}

        def watch(state):
            dd('zk node state changed to: ', state)
            sess['acquired'] = False

        self.zk.add_listener(watch)

        # test zk close

        l = zkutil.ZKLock('foo_name', zkclient=self.zk)

        l.acquire()
        self.zk.stop()
        time.sleep(0.1)
        self.assertFalse(sess['acquired'])

        # test node delete

        sess['acquired'] = True
        self.zk.start()
        self.zk.add_listener(watch)

        l = zkutil.ZKLock('foo_name', zkclient=self.zk)

        with l:
            time.sleep(0.1)
            self.zk.delete(l.zkconf.lock('foo_name'))
            time.sleep(0.1)
            self.assertFalse(sess['acquired'])

    def test_node_change_after_acquired(self):

        sess = {'acquired': True}

        def on_lost():
            sess['acquired'] = False

        l = zkutil.ZKLock('foo_name',
                          zkclient=self.zk,
                          on_lost=on_lost)

        with l:
            sess['acquired'] = True
            self.zk.delete(l.zkconf.lock('foo_name'))
            time.sleep(0.1)
            self.assertFalse(sess['acquired'])

        l = zkutil.ZKLock('foo_name',
                          zkclient=self.zk,
                          on_lost=on_lost)

        with l:
            sess['acquired'] = True
            self.zk.set(l.zkconf.lock('foo_name'), 'xxx')
            time.sleep(0.1)
            self.assertFalse(sess['acquired'])

    def test_node_change_after_released(self):

        sess = {'acquired': True}

        def on_lost():
            sess['acquired'] = False

        l = zkutil.ZKLock('foo_name',
                          zkclient=self.zk,
                          on_lost=on_lost)

        with l:
            sess['acquired'] = True

        time.sleep(0.1)
        self.assertTrue(sess['acquired'])

    def test_is_locked(self):

        l = zkutil.ZKLock('foo_name', zkclient=self.zk)

        with l:
            pass

        self.assertFalse(l.is_locked())

        l = zkutil.ZKLock('foo_name', zkclient=self.zk)
        l.acquire()
        self.assertTrue(l.is_locked())
        l.try_release()
        self.assertFalse(l.is_locked())

    def test_conn_lost_when_blocking_acquiring(self):

        l2 = zkutil.ZKLock('foo_name', on_lost=lambda: True)

        th = threadutil.start_daemon(target=self.zk.stop, after=0.5)
        with l2:
            try:
                self.lck.acquire(timeout=1)
                self.fail('expected connection error')
            except ConnectionClosedError:
                pass

        th.join()

    def test_internal_zkclient(self):

        sess = {'acquired': True}

        def on_lost():
            sess['acquired'] = False

        # There must be a listener specified to watch connection issue
        self.assertRaises(ValueError, zkutil.ZKLock, 'foo_name')

        l = zkutil.ZKLock('foo_name', on_lost=on_lost)

        with l:
            self.zk.delete(l.zkconf.lock('foo_name'))
            time.sleep(0.1)
            self.assertFalse(sess['acquired'])

    def test_acl(self):
        with self.lck:
            acls, zstat = self.zk.get_acls(self.lck.lock_path)

        dd(acls)
        self.assertEqual(1, len(acls))

        acl = acls[0]
        expected = zkutil.perm_to_long(zk_test_acl[0][2], lower=False)

        self.assertEqual(set(expected), set(acl.acl_list))
        self.assertEqual('digest', acl.id.scheme)
        self.assertEqual(zk_test_acl[0][0], acl.id.id.split(':')[0])

    def test_config(self):

        old = (config.zk_acl, config.zk_auth, config.zk_node_id)

        config.zk_acl = (('foo', 'bar', 'cd'),
                         ('xp', '123', 'cdrwa'))

        config.zk_auth = ('digest', 'xp', '123')
        config.zk_node_id = 'abc'

        l = zkutil.ZKLock('foo_name', on_lost=lambda: True)

        dd(l.zkconf.acl())

        def _check_ac(ac):
            self.assertEqual('digest', ac.id.scheme)
            self.assertEqual('foo', ac.id.id.split(':')[0])
            self.assertEqual(set(['CREATE', 'DELETE']), set(ac.acl_list))

        _check_ac(l.zkconf.kazoo_digest_acl()[0])

        with l:
            # should have created lock node
            data, zstate = self.zk.get(l.lock_path)
            dd(data)

            self.assertEqual('abc', data.split('-')[0])

            acls, zstate = self.zk.get_acls(l.lock_path)
            dd(acls)

            _check_ac(acls[0])

        (config.zk_acl, config.zk_auth, config.zk_node_id) = old

    def test_hosts(self):

        l = zkutil.ZKLock('foo_name',
                          zkconf=dict(
                              hosts='127.0.0.1:2181',
                          ),
                          on_lost=lambda: True)

        with l:
            self.assertEqual('127.0.0.1:2181', l._hosts)

    def test_specify_identifier(self):

        a = zkutil.ZKLock('foo_name',
                          zkconf=dict(
                              hosts='127.0.0.1:2181',
                          ),
                          identifier='faked',
                          on_lost=lambda: True)

        b = zkutil.ZKLock('foo_name',
                          zkconf=dict(
                              hosts='127.0.0.1:2181',
                          ),
                          identifier='faked',
                          on_lost=lambda: True)

        a.acquire()
        b.acquire()
        dd('a and b has the same identifier thus they both can acquire the lock')

    def test_release_listener_removed(self):

        self.lck.release()
        self.assertNotIn(self.lck.on_connection_change, self.zk.state_listeners)

    def test_release_owning_client_stopped(self):

        l = zkutil.ZKLock('foo_name',
                          zkconf=dict(
                              hosts='127.0.0.1:2181',
                          ),
                          on_lost=lambda: True)

        l.release()
        self.assertTrue(l.zkclient._stopped.is_set())
