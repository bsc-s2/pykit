
from kazoo.exceptions import BadVersionError
from kazoo.exceptions import NoNodeError

from pykit import utfjson
from pykit import ututil
from pykit import zktx
from pykit import zkutil
from pykit.zktx.test import base

dd = ututil.dd


class TestZKStorage(base.ZKTestBase):

    def setUp(self):
        super(TestZKStorage, self).setUp()

        self.zk.create('tx', 'tx')
        self.zk.create('lock', '{}')
        self.zk.create('tx/journal', '{}')
        self.zk.create('record', '{}')

        zke, _ = zkutil.kazoo_client_ext(self.zk)
        self.zs = zktx.ZKStorage(zke)

    def test_journal(self):

        self.zs.journal.create(1, {'a': 'b'})

        rst, ver = self.zs.journal.get(1)
        self.assertEqual({'a': 'b'}, rst)

        rst, ver = self.zk.get('tx/journal/journal_id0000000001')
        self.assertEqual({'a': 'b'}, utfjson.load(rst))

        self.assertRaises(BadVersionError, self.zs.journal.delete, 1, version=100)
        self.zs.journal.delete(1, version=0)

        self.assertRaises(NoNodeError, self.zs.journal.get, 1)

    def test_record(self):

        # nonode_callback
        rst, ver = self.zs.record.get('foo')
        self.assertEqual([None], rst)

        self.zs.record.create('foo', [(1, 1)])

        # record_load
        rst, ver = self.zs.record.get('foo')
        self.assertEqual([[1, 1]], rst)

        self.zs.record.set('foo', [(1, 2)])
        rst, ver = self.zs.record.get('foo')
        self.assertEqual([[1, 2]], rst)

    def test_lock(self):

        for holder, ver in self.zs.acquire_key_loop(2, 'foo', 10):
            exp_holder = zkutil.make_identifier(2, None)
            self.assertDictEqual(
                exp_holder, holder, "should not yield other lock holder")

        for holder, ver in self.zs.acquire_key_loop(2, 'foo', 10):
            exp_holder = zkutil.make_identifier(2, None)
            self.assertDictEqual(
                exp_holder, holder, "lock twice should be allowed.")

        try:
            for holder, ver in self.zs.acquire_key_loop(3, 'foo', 0.1):
                self.assertEqual(zkutil.make_identifier(2, None), holder)
            self.fail('expect lock timeout')
        except zkutil.LockTimeout:
            pass

        # release

        released, txid, ver = self.zs.try_release_key(3, 'foo')
        self.assertEqual((False, 2), (released, txid))

        released, txid, ver = self.zs.try_release_key(2, 'foo')
        self.assertEqual((True, 2), (released, txid))

        # duplicated release
        released, txid, ver = self.zs.try_release_key(2, 'foo')
        self.assertEqual((True, 2), (released, txid))

    def test_set_lock_key_val(self):
        holder, ver = None, None
        for holder, ver in self.zs.acquire_key_loop(4, 'foox', 10):
            pass
        self.assertDictEqual(holder, zkutil.make_identifier(4, None))

        self.zs.set_lock_key_val(4, 'foox', 'xxx_val')

        for holder, ver in self.zs.acquire_key_loop(4, 'foox', 10):
            pass
        self.assertDictEqual(holder, zkutil.make_identifier(4, 'xxx_val'))
