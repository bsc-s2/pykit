import unittest

from kazoo.client import KazooClient
from kazoo.exceptions import BadVersionError
from kazoo.exceptions import NoNodeError

from pykit import utdocker
from pykit import ututil
from pykit import zktx

dd = ututil.dd

zk_tag = 'daocloud.io/zookeeper:3.4.10'
zk_name = 'zk_test'


class ZKTestBase(unittest.TestCase):
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


class TestZKKVAccessor(ZKTestBase):

    def test_get_path(self):

        kv = zktx.ZKKeyValue(self.zk, get_path=lambda x: 'foo-' + x)

        kv.create('bar', '1')

        rst, ver = self.zk.get('foo-bar')
        self.assertEqual('1', rst)

        rst, ver = kv.get('bar')
        self.assertEqual('1', rst)

        kv.set('bar', '2')
        rst, ver = kv.get('bar')
        self.assertEqual('2', rst)

        kv.delete('bar')
        self.assertRaises(NoNodeError, kv.get, 'bar')

    def test_load(self):

        kv = zktx.ZKKeyValue(self.zk, load=lambda v: '(' + v + ')')

        self.zk.create('foo', '1')
        rst, ver = kv.get('foo')
        self.assertEqual('(1)', rst)

    def test_dump(self):

        kv = zktx.ZKKeyValue(self.zk, dump=lambda v: '(' + v + ')')

        kv.create('foo', '1')
        rst, ver = self.zk.get('foo')
        self.assertEqual('(1)', rst)

        kv.set('foo', '2')
        rst, ver = self.zk.get('foo')
        self.assertEqual('(2)', rst)

    def test_nonode_callback(self):

        kv = zktx.ZKKeyValue(self.zk, nonode_callback=lambda: ('default', 10))

        rst, ver = kv.get('foo')
        self.assertEqual(('default', 10), (rst, ver))

    def test_version(self):

        kv = zktx.ZKKeyValue(self.zk, get_path=lambda x: 'foo-' + x)

        self.zk.create('foo-bar', '1')

        kv.set('bar', '2', version=0)
        rst, ver = kv.get('bar')
        self.assertEqual('2', rst)

        self.assertRaises(BadVersionError, kv.set, 'bar', '2', version=0)
        self.assertRaises(BadVersionError, kv.set, 'bar', '2', version=2)

        self.assertRaises(BadVersionError, kv.delete, 'bar', version=0)
        self.assertRaises(BadVersionError, kv.delete, 'bar', version=2)

        kv.delete('bar')


class TestZKValueAccessor(ZKTestBase):

    def test_get_path(self):

        v = zktx.ZKValue(self.zk, get_path=lambda: 'foopath')

        v.create('1')

        rst, ver = self.zk.get('foopath')
        self.assertEqual('1', rst)

        rst, ver = v.get()
        self.assertEqual('1', rst)

        v.set('2')
        rst, ver = v.get()
        self.assertEqual('2', rst)

        v.delete()
        self.assertRaises(NoNodeError, v.get)

    def test_load(self):

        v = zktx.ZKValue(self.zk, get_path=lambda: 'foopath',
                         load=lambda v: '(' + v + ')')

        self.zk.create('foopath', '1')
        rst, ver = v.get()
        self.assertEqual('(1)', rst)

    def test_dump(self):

        v = zktx.ZKValue(self.zk, get_path=lambda: 'foopath',
                         dump=lambda v: '(' + v + ')')

        v.create('1')
        rst, ver = self.zk.get('foopath')
        self.assertEqual('(1)', rst)

        v.set('2')
        rst, ver = self.zk.get('foopath')
        self.assertEqual('(2)', rst)

    def test_nonode_callback(self):

        v = zktx.ZKValue(self.zk, get_path=lambda: 'foopath',
                         nonode_callback=lambda: ('default', 10))

        rst, ver = v.get()
        self.assertEqual(('default', 10), (rst, ver))

    def test_version(self):

        kv = zktx.ZKValue(self.zk, get_path=lambda: 'foopath')

        self.zk.create('foopath', '1')

        kv.set('2', version=0)
        rst, ver = kv.get()
        self.assertEqual('2', rst)

        self.assertRaises(BadVersionError, kv.set, '2', version=0)
        self.assertRaises(BadVersionError, kv.set, '2', version=2)

        self.assertRaises(BadVersionError, kv.delete, version=0)
        self.assertRaises(BadVersionError, kv.delete, version=2)

        kv.delete()
