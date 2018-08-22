#!/usr/bin/env python2
# coding: utf-8

import unittest
import time

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError
from pykit import utdocker
from pykit import utfjson
from pykit import zkutil
from pykit import threadutil

zk_test_name = 'zk_test'
zk_test_tag = 'daocloud.io/zookeeper:3.4.10'


class TestCachedReader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        utdocker.pull_image(zk_test_tag)

    def setUp(self):
        utdocker.create_network()
        utdocker.start_container(
            zk_test_name,
            zk_test_tag,
            env={
                "ZOO_MY_ID": 1,
                "ZOO_SERVERS": "server.1=0.0.0.0:2888:3888",
            },
            port_bindings={
                2181: 21811,
            }
        )

        self.zk = KazooClient(hosts='127.0.0.1:21811')
        self.zk.start()
        self.val = {'a': 1, 'b': 2}
        self.zk.create('foo', utfjson.dump(self.val))

    def tearDown(self):
        self.zk.stop()
        utdocker.remove_container(zk_test_name)

    def test_cache(self):
        c = zkutil.CachedReader(self.zk, 'foo')
        self.assertDictEqual(self.val, c)

    def test_cb(self):
        latest = ['foo']

        def cb(path, old, new):
            latest[0] = new

        zkutil.CachedReader(self.zk, 'foo', callback=cb)

        for i in range(100):
            self.val['a'] += 1
            self.zk.set('foo', utfjson.dump(self.val))

        time.sleep(1)
        self.assertEqual(self.val, latest[0])

    def test_update(self):
        c = zkutil.CachedReader(self.zk, 'foo')
        self.assertDictEqual(self.val, c)

        cases = (
            {'a': 2},
            {'a': 'a_v', 'b': 'b_v'},
            {'a': 3, 'b': {'c': 4}, 'd': {'e': {'e': 'val'}}},
        )

        for case in cases:
            self.zk.set('foo', utfjson.dump(case))
            time.sleep(0.5)
            self.assertDictEqual(case, c)

    def test_ex(self):
        try:
            zkutil.CachedReader(self.zk, 'bar')
            self.assertFalse(True, 'should raise a NoNodeError')
        except NoNodeError:
            pass

        c = zkutil.CachedReader(self.zk, 'foo')
        self.assertRaises(zkutil.ZKWaitTimeout, c.watch, 1)

    def test_watch(self):
        val = {'a': 2}
        c = zkutil.CachedReader(self.zk, 'foo')

        def _change_node():
            self.zk.set('foo', utfjson.dump(val))

        threadutil.start_daemon(_change_node, after=1)
        self.assertEqual([self.val, val], c.watch())

        def _close():
            c.close()

        threadutil.start_daemon(_close, after=1)
        self.assertEqual(None, c.watch())
