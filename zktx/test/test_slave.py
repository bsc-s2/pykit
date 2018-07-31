#!/usr/bin/env python
# coding: utf-8

from pykit import rangeset
from pykit import redisutil
from pykit import utdocker
from pykit import ututil
from pykit import zktx
from pykit import zkutil
from pykit.zktx.status import COMMITTED
from pykit.zktx.test import base

dd = ututil.dd

redis_tag = 'daocloud.io/redis:3.2.3'
redis_port = 6379

zk_tag = 'daocloud.io/zookeeper:3.4.10'
zk_name = 'zk_test'


class TestSlave(base.ZKTestBase):

    @classmethod
    def setUpClass(cls):
        utdocker.pull_image(redis_tag)
        utdocker.pull_image(zk_tag)

    def setUp(self):
        super(TestSlave, self).setUp()
        utdocker.create_network()

        utdocker.start_container('redis-0', redis_tag, '192.168.52.40', '')
        dd('started redis in docker')

        redisutil.wait_serve(('192.168.52.40', redis_port))
        self.redis_cli = redisutil.get_client(('192.168.52.40', redis_port))

        self.journal_id_path = "tx/journal_id_set"
        self.storage = zktx.RedisStorage(self.redis_cli, self.journal_id_path)

        self.zk.create('tx', 'tx')
        self.zk.create('tx/journal_id_set', '{}')
        self.zk.create('tx/alive', '{}')
        self.zk.create('tx/txid_maker', '{}')
        self.zk.create('tx/journal', '{}')

        for d in ('lock', 'record'):
            self.zk.create(d, '{}')
            for d1 in ('leader', 'meta', 'job'):
                self.zk.create('/'.join([d, d1]), '{}')
                for d2 in ('block_group', 'global', 'region', 'server'):
                    self.zk.create('/'.join([d, d1, d2]), '{}')

        self.zke, _ = zkutil.kazoo_client_ext(self.zk)

        self.slave = zktx.Slave(self.zke, self.storage)

    def tearDown(self):
        utdocker.remove_container('redis-0')
        utdocker.remove_container(zk_name)

    def _dump_to_zk(self, kv):
        with zktx.ZKTransaction(self.zk) as t1:

            for k, v in kv.items():
                r = t1.lock_get(k)
                r.v = v
                t1.set(r)

            t1.commit()

    def test_apply(self):
        cases = (
            {'meta/server/k1': 10, 'meta/region/k2': 100},
            {'meta/server/k3': 'server_v1', 'meta/region/k4': 'region_v2'},

            {'meta/server/k5': {}, 'meta/region/k6': {}},
            {'meta/server/k7': {'x': 'x', 'y': 'y'}, 'meta/region/k8': {'x': 'x', 'y': 'y'}},

            {'meta/server/k9': [], 'meta/region/k10': []},
            {'meta/server/k11': [1, 2], 'meta/region/k12': [4, 5]},
        )

        max_journal_id = 0
        for c in cases:
            self._dump_to_zk(c)
            cmt_journal_id_set = self.storage.journal_id_set.get()[COMMITTED]

            if max_journal_id == 0:
                self.assertEqual([], cmt_journal_id_set)

            self.slave.apply()

            for k, v in c.items():
                k_parts = k.split('/', 2)
                actual_val = self.storage.record.hget(k_parts[1], k_parts[2])
                self.assertEqual(v, actual_val)

            ex = rangeset.RangeSet([[0, max_journal_id + 1]])
            cmt_journal_id_set = self.storage.journal_id_set.get()[COMMITTED]
            self.assertEqual(ex, cmt_journal_id_set)

            max_journal_id += 1

        # no update
        self.slave.apply()
        ex = rangeset.RangeSet([[0, max_journal_id]])
        cmt_journal_id_set = self.storage.journal_id_set.get()[COMMITTED]
        self.assertEqual(ex, cmt_journal_id_set)

    def test_jour_not_found(self):
        c = {
            'meta/server/k1': 1,
            'meta/server/k2': 'server_v1',
            'meta/server/k3': {},
            'meta/server/k4': {'x': 'x'},
            'meta/server/k5': [],
            'meta/server/k6': [1, 'x'],

            'meta/region/k1': 1,
            'meta/region/k2': 'region_v1',
            'meta/region/k3': {},
            'meta/region/k4': {'x': 'x'},
            'meta/region/k5': [],
            'meta/region/k6': [1, 'x'],
        }

        self._dump_to_zk(c)

        self.zk.delete('tx/journal/journal_id0000000000')

        self.slave.apply()

        for k, v in c.items():
            k_parts = k.split('/', 2)
            actual_val = self.storage.record.hget(k_parts[1], k_parts[2])
            self.assertEqual(v, actual_val)

        ex = rangeset.RangeSet([[0, 1]])
        cmt_journal_id_set = self.storage.journal_id_set.get()[COMMITTED]
        self.assertEqual(ex, cmt_journal_id_set)

        # apply
        c = {
            'meta/server/k1': 100,
        }
        self._dump_to_zk(c)
        self.slave.apply()

        ex = rangeset.RangeSet([[0, 2]])
        cmt_journal_id_set = self.storage.journal_id_set.get()[COMMITTED]
        self.assertEqual(ex, cmt_journal_id_set)

        actual_val = self.storage.record.hget('server', 'k1')
        self.assertEqual(100, actual_val)

    def test_delete_use_journal(self):
        c = {
            'meta/region/001': 1,
        }
        self._dump_to_zk(c)

        self.slave.apply()
        self.assertEqual(1, self.storage.record.hget('region', '001'))

        c = {
            'meta/region/001': None,
        }
        self._dump_to_zk(c)

        self.slave.apply()
        self.assertEqual(None, self.storage.record.hget('region', '001'))

    def test_delete_not_use_journal(self):
        c = {
            'meta/region/001': 1,
        }
        self._dump_to_zk(c)

        self.slave.apply()
        self.assertEqual(1, self.storage.record.hget('region', '001'))
        self.zk.delete('tx/journal/journal_id0000000000')

        c = {
            'meta/region/001': None,
        }
        self._dump_to_zk(c)
        self.zk.delete('tx/journal/journal_id0000000001')
        self.slave.apply()
        self.assertEqual(None, self.storage.record.hget('region', '001'))
