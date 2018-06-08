
from kazoo.exceptions import BadVersionError
from kazoo.exceptions import NoNodeError

from pykit import ututil
from pykit import zktx
from pykit.zktx.test import base

dd = ututil.dd


class TestZKKVAccessor(base.ZKTestBase):

    def test_set_or_create_acl(self):

        kv = zktx.ZKKeyValue(self.zkauthed)

        kv.set_or_create('tacl', '1')

        acl, _ = self.zkauthed.get_acls('tacl')

        self.assertEqual(acl, self.zkauthed._zkconf.kazoo_digest_acl())

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

    def test_set_or_create(self):

        kv = zktx.ZKKeyValue(self.zk)

        # create

        kv.set_or_create('foo', '1')

        rst, ver = kv.get('foo')
        self.assertEqual('1', rst)
        self.assertEqual(0, ver)

        # set

        self.assertRaises(BadVersionError, kv.set_or_create, 'foo', '2', version=2)

        kv.set_or_create('foo', '2', version=0)
        kv.set_or_create('foo', '2', version=1)
        rst, ver = kv.get('foo')
        self.assertEqual('2', rst)
        self.assertEqual(2, ver)


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

        v = zktx.ZKValue(self.zk, get_path=lambda: 'foopath')

        self.zk.create('foopath', '1')

        v.set('2', version=0)
        rst, ver = v.get()
        self.assertEqual('2', rst)

        self.assertRaises(BadVersionError, v.set, '2', version=0)
        self.assertRaises(BadVersionError, v.set, '2', version=2)

        self.assertRaises(BadVersionError, v.delete, version=0)
        self.assertRaises(BadVersionError, v.delete, version=2)

        v.delete()

    def test_set_or_create(self):

        v = zktx.ZKValue(self.zk, get_path=lambda: 'foopath')

        # create

        v.set_or_create('1')

        rst, ver = v.get()
        self.assertEqual('1', rst)
        self.assertEqual(0, ver)

        # set

        self.assertRaises(BadVersionError, v.set_or_create, '2', version=2)

        v.set_or_create('2', version=0)
        v.set_or_create('2', version=1)
        rst, ver = v.get()
        self.assertEqual('2', rst)
        self.assertEqual(2, ver)

    def test_set_or_create_acl(self):
        v = zktx.ZKValue(self.zkauthed, get_path=lambda: 'taclvalue')

        # create

        v.set_or_create('1')

        acl, _ = self.zkauthed.get_acls('taclvalue')
        self.assertEqual(acl, self.zkauthed._zkconf.kazoo_digest_acl())
