import unittest

from kazoo.client import KazooClient

from pykit import threadutil
from pykit import utdocker
from pykit import ututil
from pykit import zkutil

dd = ututil.dd

zk_tag = 'daocloud.io/zookeeper:3.4.10'
zk_name = 'zk_test'


class TestAcid(unittest.TestCase):

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

        self.path = 'a'
        self.zk.create(self.path, '1')

    def tearDown(self):

        self.zk.stop()
        utdocker.remove_container(zk_name)

    def test_cas(self):

        for curr, set_val in zkutil.cas_loop(self.zk, self.path):
            set_val(curr + 2)

        final_val, zstat = self.zk.get(self.path)
        dd(final_val, zstat)
        self.assertEqual('3', final_val)

    def test_cas_create_zk(self):

        for first_arg in (
                '127.0.0.1:2181',
                {'hosts': '127.0.0.1:2181'},
                zkutil.ZKConf(hosts='127.0.0.1:2181'),
        ):
            self.zk.set(self.path, '1')

            for curr, set_val in zkutil.cas_loop(first_arg, self.path):
                set_val(curr + 2)

            final_val, zstat = self.zk.get(self.path)
            dd(final_val, zstat)
            self.assertEqual('3', final_val)

    def test_cas_non_json(self):

        for curr, set_val in zkutil.cas_loop(self.zk, self.path, json=False):
            self.assertIsInstance(curr, str)
            set_val(curr + "a")

        final_val, zstat = self.zk.get(self.path)
        dd(final_val, zstat)
        self.assertEqual('1a', final_val)

    def test_cas_concurrent(self):

        def _update():
            for ii in range(10):
                for curr, set_val in zkutil.cas_loop('127.0.0.1:2181', self.path):
                    set_val(curr + 1)

        ths = [threadutil.start_daemon(_update)
               for _ in range(5)]

        for th in ths:
            th.join()

        final_val, zstat = self.zk.get(self.path)
        dd(final_val, zstat)

        self.assertEqual('51', final_val)
