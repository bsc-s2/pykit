import unittest

from kazoo.client import KazooClient

from pykit import utdocker
from pykit import ututil
from pykit import zkutil

dd = ututil.dd

zk_tag = 'daocloud.io/zookeeper:3.4.10'
zk_name = 'zk_test'


class ZKTestBase(unittest.TestCase):
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

        self.zkauthed, _ = zkutil.kazoo_client_ext(
            {'hosts': '127.0.0.1:2181', 'auth': ('digest', 'xp', '123'),
             'acl': (('xp', '123', 'cdrwa'), ('foo', 'bar', 'rw'))})

        dd('start zk-test in docker')

    def tearDown(self):

        self.zk.stop()
        self.zkauthed.stop()
        utdocker.remove_container(zk_name)
