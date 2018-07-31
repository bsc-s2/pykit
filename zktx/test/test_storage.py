import threading
import unittest

from kazoo.exceptions import BadVersionError

from pykit import rangeset
from pykit import ututil
from pykit import zktx
from pykit.zktx import COMMITTED
from pykit.zktx import PURGED

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

    def safe_delete(self, key, version=None):
        # for test of purge
        pass


class JournalidsetAccessor(object):
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

        self.journal_id_set = JournalidsetAccessor()

        self.journal = PseudoKVAccessor({})


class TestTXStorageHelper(unittest.TestCase):

    def setUp(self):
        self.sto = PseudoStorage()

    def _rand_journal_ids(self):
        for ii in range(100):
            journal_id = int(ii % 53 * 1.3)
            yield journal_id

    def test_add_to_journal_id_set(self):
        self.assertRaises(KeyError, self.sto.add_to_journal_id_set, 'foo', 1)

        cases = (1, 30, 100, 1000)
        for jid in cases:
            self.sto.add_to_journal_id_set(COMMITTED, jid)
            rst, ver = self.sto.journal_id_set.get()
            for i in range(jid):
                self.assertTrue(rst[COMMITTED].has(i))

        expected = {jid: True
                    for jid in self._rand_journal_ids()}

        for jid in self._rand_journal_ids():
            self.sto.add_to_journal_id_set(PURGED, jid)

        rst, ver = self.sto.journal_id_set.get()

        for journal_id in expected:
            self.assertTrue(rst[PURGED].has(journal_id))

        for journal_id in range(100):
            if journal_id not in expected:
                self.assertFalse(rst[PURGED].has(journal_id))

    def test_purge(self):

        self.sto.max_journal_history = 5

        cases = (
                (
                    {PURGED: [],        COMMITTED: [[0, 100]]},
                    {PURGED: [[0, 95]], COMMITTED: [[0, 100]]},
                ),
                (
                    {PURGED: [[1, 10]],  COMMITTED: [[0, 200]]},
                    {PURGED: [[0, 195]], COMMITTED: [[0, 200]]},
                ),
                # no need to purge
                (
                    {PURGED: [[0, 95]], COMMITTED: [[0, 100]]},
                    {PURGED: [[0, 95]], COMMITTED: [[0, 100]]},
                ),
        )

        for inp, expected in cases:
            inp = {k: rangeset.RangeSet(v) for k, v in inp.items()}
            self.sto.purge(inp)
            self.assertEqual(expected, inp)
