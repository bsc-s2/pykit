
from kazoo.exceptions import BadVersionError
from kazoo.exceptions import NoNodeError

from pykit import ututil
from pykit import zktx
from pykit.zktx.test import base

dd = ututil.dd


class TestZKKVAccessor(base.ZKTestBase):

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


class TestZKValueAccessor(base.ZKTestBase):

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
