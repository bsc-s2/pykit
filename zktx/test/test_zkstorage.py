
from kazoo.exceptions import BadVersionError
from kazoo.exceptions import NoNodeError

from pykit import utfjson
from pykit import ututil
from pykit import zktx
from pykit import zkutil
from pykit.zktx import COMMITTED
from pykit.zktx.test import base

dd = ututil.dd


class TestZKStorage(base.ZKTestBase):

    def setUp(self):
        super(TestZKStorage, self).setUp()

        self.zk.create('tx', 'tx')
        self.zk.create('lock', '{}')
        self.zk.create('tx/txidset', '{}')
        self.zk.create('tx/journal', '{}')
        self.zk.create('record', '{}')

        zke, _ = zkutil.kazoo_client_ext(self.zk)
        self.zs = zktx.ZKStorage(zke)

    def test_txidset(self):

        self.zs.add_to_txidset(COMMITTED, 1)
        rst, ver = self.zs.txidset.get()

        self.assertEqual({COMMITTED: [[1, 2]]}, rst)

    def test_journal(self):

        self.zs.journal.create(1, {'a': 'b'})

        rst, ver = self.zs.journal.get(1)
        self.assertEqual({'a': 'b'}, rst)

        rst, ver = self.zk.get('tx/journal/0000000001')
        self.assertEqual({'a': 'b'}, utfjson.load(rst))

        self.assertRaises(BadVersionError, self.zs.journal.delete, 1, version=100)
        self.zs.journal.delete(1, version=0)

        self.assertRaises(NoNodeError, self.zs.journal.get, 1)

    def test_record(self):

        self.zs.record.create('foo', {1: 1})

        rst, ver = self.zs.record.get('foo')
        self.assertEqual({1: 1}, rst)

        self.zs.record.set('foo', {1: 2})
        rst, ver = self.zs.record.get('foo')
        self.assertEqual({1: 2}, rst)

        self.zs.apply_record(2, 'foo', 3)
        rst, ver = self.zs.record.get('foo')
        self.assertEqual({1: 2, 2: 3}, rst)

        rst, ver = self.zs.get_latest('foo')
        self.assertEqual({2: 3}, rst)

    def test_lock(self):

        locked, txid, ver = self.zs.try_lock_key(2, 'foo')
        self.assertEqual((True, 2), (locked, txid))

        locked, txid, ver = self.zs.try_lock_key(2, 'foo')
        self.assertEqual((True, 2), (locked, txid), 'relock by the same txid')

        locked, txid, ver = self.zs.try_lock_key(3, 'foo')
        self.assertEqual((False, 2), (locked, txid))

        # release

        released, txid, ver = self.zs.try_release_key(3, 'foo')
        self.assertEqual((False, 2), (released, txid))

        released, txid, ver = self.zs.try_release_key(2, 'foo')
        self.assertEqual((True, 2), (released, txid))

        # duplicated release
        released, txid, ver = self.zs.try_release_key(2, 'foo')
        self.assertEqual((True, 2), (released, txid))
