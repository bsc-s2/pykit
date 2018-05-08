import unittest

from pykit import config
from pykit import ututil
from pykit import zkutil

dd = ututil.dd


class TestZKConf(unittest.TestCase):

    def test_specified(self):

        c = zkutil.ZKConf(
            hosts='hosts',
            journal_dir='journal_dir/',
            record_dir='record_dir/',
            lock_dir='lock_dir/',
            auth=('digest', 'a', 'b'),
            acl='acl'
        )

        self.assertEqual('hosts',       c.hosts())
        self.assertEqual('journal_dir/', c.journal_dir())
        self.assertEqual('record_dir/',  c.record_dir())
        self.assertEqual('lock_dir/',    c.lock_dir())
        self.assertEqual(('digest', 'a', 'b'),        c.auth())
        self.assertEqual('acl',         c.acl())

        self.assertEqual('lock_dir/', c.lock())
        self.assertEqual('lock_dir/a', c.lock('a'))
        self.assertEqual('record_dir/', c.record())
        self.assertEqual('record_dir/a', c.record('a'))
        self.assertEqual('journal_dir/tx_alive/', c.tx_alive())
        self.assertEqual('journal_dir/tx_alive/a', c.tx_alive('a'))
        self.assertEqual('journal_dir/tx/', c.tx())
        self.assertEqual('journal_dir/tx/a', c.tx('a'))
        self.assertEqual('journal_dir/txid_range', c.txid_range())

        self.assertEqual(('digest', 'a:b'), c.kazoo_auth())

    def test_default(self):
        old = (
            config.zk_hosts,
            config.zk_journal_dir,
            config.zk_record_dir,
            config.zk_lock_dir,
            config.zk_auth,
            config.zk_acl,
        )

        config.zk_hosts = 'HOSTS'
        config.zk_journal_dir = 'JOURNAL_DIR/'
        config.zk_record_dir = 'RECORD_DIR/'
        config.zk_lock_dir = 'LOCK_DIR/'
        config.zk_auth = ('DIGEST', 'A', 'B')
        config.zk_acl = 'ACL'

        c = zkutil.ZKConf()

        self.assertEqual('HOSTS',       c.hosts())
        self.assertEqual('JOURNAL_DIR/', c.journal_dir())
        self.assertEqual('RECORD_DIR/',  c.record_dir())
        self.assertEqual('LOCK_DIR/',    c.lock_dir())
        self.assertEqual(('DIGEST', 'A', 'B'),        c.auth())
        self.assertEqual('ACL',         c.acl())

        self.assertEqual('LOCK_DIR/', c.lock())
        self.assertEqual('LOCK_DIR/a', c.lock('a'))
        self.assertEqual('RECORD_DIR/', c.record())
        self.assertEqual('RECORD_DIR/a', c.record('a'))
        self.assertEqual('JOURNAL_DIR/tx_alive/', c.tx_alive())
        self.assertEqual('JOURNAL_DIR/tx_alive/a', c.tx_alive('a'))
        self.assertEqual('JOURNAL_DIR/tx/', c.tx())
        self.assertEqual('JOURNAL_DIR/tx/a', c.tx('a'))
        self.assertEqual('JOURNAL_DIR/txid_range', c.txid_range())

        self.assertEqual(('DIGEST', 'A:B'), c.kazoo_auth())

        (
            config.zk_hosts,
            config.zk_journal_dir,
            config.zk_record_dir,
            config.zk_lock_dir,
            config.zk_auth,
            config.zk_acl,
        ) = old
