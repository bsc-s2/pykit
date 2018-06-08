#!/usr/bin/env python
# coding: utf-8

import unittest

from pykit import redisutil
from pykit import utdocker
from pykit import utfjson
from pykit import ututil
from pykit import zktx
from pykit.zktx.status import COMMITTED

dd = ututil.dd

redis_tag = 'daocloud.io/redis:3.2.3'
redis_port = 6379


class TestRedis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        utdocker.pull_image(redis_tag)

    def setUp(self):
        utdocker.create_network()

        utdocker.start_container('redis-0', redis_tag, '192.168.52.40', '')
        dd('started redis in docker')

        redisutil.wait_serve(('192.168.52.40', redis_port))

        self.redis_cli = redisutil.get_client(('192.168.52.40', redis_port))
        self.txid_path = "tx/txidset"
        self.storage = zktx.RedisStorage(self.redis_cli, self.txid_path)

    def tearDown(self):
        utdocker.remove_container('redis-0')

    def test_kv_get_set(self):
        accessor = zktx.RedisKeyValue(self.redis_cli)

        cases = (
            ('k1', 1),
            ('k2', {}),
            ('k3', []),
            ('k4', 'foo'),
            ('k5', {"xx": "xx"}),
            ('k6', [1, 2]),
        )

        for k, v in cases:
            accessor.set(k, v)
            actual = accessor.get(k)
            self.assertEqual(v, actual)

    def test_kv_hget_hset(self):
        accessor = zktx.RedisKeyValue(self.redis_cli)

        cases = (
            ('h1', 'k1', 1),
            ('h2', 'k2', {}),
            ('h3', 'k3', []),
            ('h4', 'k4', 'foo'),
            ('h5', 'k5', {"xx": "xx"}),
            ('h6', 'k6', [1, 2]),
        )

        for h, k, v in cases:
            accessor.hset(h, k, v)
            actual = accessor.hget(h, k)
            self.assertEqual(v, actual)

    def test_kv_get_path(self):
        def get_path(k):
            return 'foo/' + k

        accessor = zktx.RedisKeyValue(self.redis_cli, get_path=get_path)
        cases = (
            ('k1', 1),
            ('k2', {}),
            ('k3', []),
            ('k4', 'foo'),
            ('k5', {"xx": "xx"}),
            ('k6', [1, 2]),
        )

        for k, v in cases:
            accessor.set(k, v)
            actual = self.redis_cli.get(get_path(k))
            self.assertEqual(v, utfjson.load(actual))

    def test_v_get_set(self):
        def get_path():
            return 'foo'

        accessor = zktx.RedisValue(self.redis_cli, get_path=get_path)

        cases = (
            1,
            {},
            [],
            'foo',
            {'xx': 'xx'},
            [1, 2],
        )

        for v in cases:
            accessor.set(v)
            actual = accessor.get()
            self.assertEqual(v, actual)

    def test_load(self):
        def load(val):
            return 'foo'

        accessor = zktx.RedisKeyValue(self.redis_cli, load=load)
        accessor.set('xx', 'xx')
        val = accessor.get('xx')

        self.assertEqual('foo', val)

    def test_get_txidset(self):
        cases = (
            [[1, 2]],
            [[7, 20]],
            [[1, 3], [7, 8]],
            [[1, 2], [10, 15]],
        )

        for c in cases:
            val = {
                COMMITTED: c,
            }
            self.redis_cli.delete(self.txid_path)
            self.redis_cli.set(self.txid_path, utfjson.dump(val))
            txidset = self.storage.txidset.get()
            self.assertEqual(c, txidset[COMMITTED])

    def test_apply_jour(self):
        cases = (
            {'meta/h1/k1': 1},
            {'meta/h2/k2': {}},
            {'meta/h3/k3': []},
            {'meta/h4/k4': 'foo'},
            {'meta/h5/k5': {'xx': 'xxx'}},

            {'meta/h10/k10': 1, 'meta/h100/k100': 10},
            {'meta/h11/k11': {}, 'meta/h101/k101': {}},
            {'meta/h12/k12': [], 'meta/h102/k102': []},
            {'meta/h13/k13': 'foo', 'meta/h103/k103': 'bar'},
            {'meta/h14/k14': {'xx': 'xxx'}, 'meta/h104/k104': {'yy': 'yyy'}},
        )

        for jour in cases:
            self.storage.apply_jour(jour)

            for k, v in jour.items():
                k_parts = k.split('/', 2)

                actual = self.redis_cli.hget(k_parts[1], k_parts[2])

                self.assertEqual(v, utfjson.load(actual))

    def test_set_txidset(self):
        cases = (
            [[1, 2]],
            [[7, 20]],
            [[1, 3], [7, 8]],
            [[1, 2], [10, 15]],
        )

        for c in cases:
            self.storage.set_txidset(COMMITTED, c)

            txidset = self.storage.txidset.get()
            self.assertEqual(c, txidset[COMMITTED])
