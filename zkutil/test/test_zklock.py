
import time
import unittest

from kazoo.client import KazooClient

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
        self.zk.close()
        utdocker.remove_container(zk_test_name)

    def _loop_acquire(self, ident):

        zk = KazooClient(hosts='127.0.0.1:2181')
        zk.start()
        scheme, name, passw = zk_test_auth
        zk.add_auth(scheme, name + ':' + passw)

        for ii in range(40):
            l = zkutil.ZKLock('foo_name', zkclient=zk)
            with l:

                self.counter += 1

                self.assertTrue(self.counter == 1)

                time.sleep(0.01)
                self.counter -= 1

                dd("id={ident:0>2} n={ii:0>2} got and released lock: {holder}".format(
                    ident=ident,
                    ii=ii,
                    holder=l.lock_holder))

        zk.stop()
        zk.close()

    def test_concurrent(self):

        self.running = True

        ths = []
        for ii in range(5):
            t = threadutil.start_daemon_thread(self._loop_acquire, args=(ii,))
            ths.append(t)

        for th in ths:
            th.join()

        self.running = False

    def test_timeout(self):
        l1 = zkutil.ZKLock('foo_name', on_lost=lambda: True)
        l2 = zkutil.ZKLock('foo_name', on_lost=lambda: True)
        with l1:
            t0 = time.time()
            self.assertRaises(zkutil.LockTimeout, l2.acquire, timeout=0.2)
            t1 = time.time()

            self.assertAlmostEqual(0.2, t1-t0, places=1)

    def test_zk_lost(self):

        sess = {'acquired': True}

        def watch(state):
            dd('zk node state changed to: ', state)
            sess['acquired'] = False

        self.zk.add_listener(watch)

        # test zk close

        l = zkutil.ZKLock('foo_name', zkclient=self.zk)

        with l:
            time.sleep(0.1)
            self.zk.stop()
            self.zk.close()
            time.sleep(0.1)
            self.assertFalse(sess['acquired'])

        # test node delete

        sess['acquired'] = True
        self.zk.start()
        self.zk.add_listener(watch)

        l = zkutil.ZKLock('foo_name', zkclient=self.zk)

        with l:
            time.sleep(0.1)
            self.zk.delete(l.lock_dir + 'foo_name')
            time.sleep(0.1)
            self.assertFalse(sess['acquired'])

    def test_internal_zkclient(self):

        sess = {'acquired': True}

        def on_lost():
            sess['acquired'] = False
            print sess['acquired']

        # There must be a listener specified to watch connection issue
        self.assertRaises(ValueError, zkutil.ZKLock, 'foo_name')

        l = zkutil.ZKLock('foo_name', on_lost=on_lost)

        with l:
            self.zk.delete(l.lock_dir + 'foo_name')
            time.sleep(0.3)

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

        dd(l.acl)

        def _check_ac(ac):
            self.assertEqual('digest', ac.id.scheme)
            self.assertEqual('foo', ac.id.id.split(':')[0])
            self.assertEqual(set(['CREATE', 'DELETE']), set(ac.acl_list))

        _check_ac(l.acl[0])

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
                          hosts='127.0.0.1:2181',
                          on_lost=lambda: True)

        with l:
            self.assertEqual('127.0.0.1:2181', l._hosts)
