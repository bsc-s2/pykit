import threading
import unittest

from kazoo.exceptions import BadVersionError

from pykit import rangeset
from pykit import threadutil
from pykit import ututil
from pykit import zktx
from pykit.zktx import COMMITTED
from pykit.zktx import STATUS

dd = ututil.dd

zk_tag = 'daocloud.io/zookeeper:3.4.10'
zk_name = 'zk_test'


class PseudoKVAccessor(dict):

    def __init__(self, *args, **kwargs):

        super(PseudoKVAccessor, self).__init__(*args, **kwargs)

        self.lock = threading.RLock()

    def get(self, key):

        with self.lock:
            return super(PseudoKVAccessor, self).get(key)

    def set(self, key, value, version):

        with self.lock:

            prev = self[key]
            if prev[1] != version:
                raise BadVersionError()

            self[key] = (value, version+1)

    def set_or_create(self, key, value, version):

        with self.lock:

            if key in self:
                return self.set(key, value, version)
            else:
                if version == -1:
                    self[key] = (value, 0)
                else:
                    raise BadVersionError()


class TxidsetAccessor(object):
    def __init__(self):
        self.lock = threading.RLock()
        self.ver = 0
        self.d = {}

    def get(self):
        with self.lock:
            for k in self.d:
                self.d[k] = rangeset.RangeSet(self.d[k])

            return self.d, self.ver

    def set(self, value, version=None):
        with self.lock:
            if version is not None and version != self.ver:
                raise BadVersionError()

            self.d = value
            self.ver = version + 1

    def set_or_create(self, key, value, version):
        return self.set(value, version)


class PseudoStorage(zktx.StorageHelper):

    conflicterror = BadVersionError

    def __init__(self):
        self.record = PseudoKVAccessor({
            'foo': ([[1, 1], [17, 17]], 0),
            'bar': ([[-1, None]], 1),
        })

        self.txidset = TxidsetAccessor()


class TestTXStorageHelper(unittest.TestCase):

    def setUp(self):
        self.sto = PseudoStorage()

    def test_get_latest(self):

        rst = self.sto.record.get('foo')
        self.assertEqual(([[1, 1], [17, 17]], 0), rst)

        rst = self.sto.record.get('bar')
        self.assertEqual(([[-1,  None]], 1), rst)

    def test_apply_record(self):

        cases = (
                (0,  'foo', 'fooval', (None,     0), '<=max txid'),
                (1,  'foo', 'fooval', (1,        0), '<=max txid'),
                (16, 'foo', 'fooval', (None,     0), '<=max txid'),
                (17, 'foo', 'fooval', (17,       0), '<=max txid'),
                (18, 'foo', 'fooval', ('fooval', 1), '>max txid'),
                (1,  'bar', 'barval', ('barval', 2), '>max txid'),
                (1,  'bar', 'barval', ('barval', 2), '<=max txid'),
        )

        for txid, key, value, expected, mes in cases:

            dd(txid, key, value, expected, mes)

            self.sto.apply_record(txid, key, value)

            rec, ver = self.sto.record.get(key)
            val_of_txid = dict(rec).get(txid)
            self.assertEqual(expected, (val_of_txid, ver))

    def test_apply_record_max_history(self):

        s, e = 100, 150
        for txid in range(s, e):
            self.sto.apply_record(txid, 'foo', txid)

        rec, ver = self.sto.record.get('foo')
        self.assertEqual(e-s, ver)
        self.assertEqual(self.sto.max_value_history, len(rec))

    def test_apply_record_concurrently(self):

        n_thread = 10
        n_repeat = 100

        self.sto.max_value_history = n_thread * n_repeat + 1

        l = threading.RLock()
        sess = {'txid': 0}
        success_tx = {-1: True}

        def _apply(ithread):
            for ii in range(n_repeat):

                with l:
                    sess['txid'] += 1
                    txid = sess['txid']

                if self.sto.apply_record(txid, 'bar', txid):
                    with l:
                        success_tx[txid] = True

        ths = [threadutil.start_daemon(_apply, args=(ii, ))
               for ii in range(n_thread)]

        for th in ths:
            th.join()

        rec, ver = self.sto.record.get('bar')
        dd(len(rec))
        dd(ver)

        self.assertEqual(set(success_tx.keys()),
                         set([x[0] for x in rec]))

        rec, ver = self.sto.record.get('bar')
        dd(rec, ver)

        self.assertLessEqual(ver, 1+n_thread*n_repeat)
        self.assertEqual(n_thread*n_repeat, rec[-1][0])
        self.assertEqual(n_thread*n_repeat, rec[-1][1])

    def _rand_txids(self):
        for ii in range(100):
            txid = int(ii % 53 * 1.3)
            yield txid

    def test_add_to_txidset(self):

        self.assertRaises(KeyError, self.sto.add_to_txidset, 'foo', 1)

        expected = {txid: True
                    for txid in self._rand_txids()}

        for status in STATUS:
            for txid in self._rand_txids():
                self.sto.add_to_txidset(status, txid)

            dd(sorted(expected.keys()))

            rst, ver = self.sto.txidset.get()
            dd(rst[status])

            for txid in expected:
                self.assertTrue(rst[status].has(txid))

            for txid in range(100):
                if txid not in expected:
                    self.assertFalse(rst[status].has(txid))

    def test_add_to_txidset_concurrent(self):

        expected = {txid: True
                    for txid in self._rand_txids()}

        n_thread = 2
        status = COMMITTED

        def _add():
            for txid in self._rand_txids():
                self.sto.add_to_txidset(status, txid)

        for th in [threadutil.start_daemon(_add)
                   for _ in range(n_thread)]:

            th.join()

        rst, ver = self.sto.txidset.get()
        dd(rst[status])

        for txid in expected:
            self.assertTrue(rst[status].has(txid))

        for txid in range(100):
            if txid not in expected:
                self.assertFalse(rst[status].has(txid))
