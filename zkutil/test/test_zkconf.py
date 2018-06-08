import unittest

from pykit import config
from pykit import ututil
from pykit import zkutil

dd = ututil.dd


class TestZKConf(unittest.TestCase):

    def test_specified(self):

        c = zkutil.ZKConf(
            hosts='hosts',
            tx_dir='tx_dir/',
            record_dir='record_dir/',
            seq_dir='seq_dir/',
            lock_dir='lock_dir/',
            node_id='node_id',
            auth=('digest', 'a', 'b'),
            acl=(('foo', 'bar', 'cd'), ('xp', '123', 'cdrwa'))
        )

        self.assertEqual('hosts',              c.hosts())
        self.assertEqual('tx_dir/',            c.tx_dir())
        self.assertEqual('record_dir/',        c.record_dir())
        self.assertEqual('seq_dir/',           c.seq_dir())
        self.assertEqual('lock_dir/',          c.lock_dir())
        self.assertEqual('node_id',            c.node_id())
        self.assertEqual(('digest', 'a', 'b'), c.auth())

        self.assertEqual((('foo', 'bar', 'cd'),
                          ('xp', '123', 'cdrwa')),
                         c.acl())

        self.assertEqual('lock_dir/',                 c.lock())
        self.assertEqual('lock_dir/a',                c.lock('a'))
        self.assertEqual('record_dir/',               c.record())
        self.assertEqual('record_dir/a',              c.record('a'))
        self.assertEqual('tx_dir/alive/',             c.tx_alive())
        self.assertEqual('tx_dir/alive/a',            c.tx_alive('a'))
        self.assertEqual('tx_dir/alive/0000000001',   c.tx_alive(1))
        self.assertEqual('tx_dir/state/',             c.tx_state())
        self.assertEqual('tx_dir/state/a',            c.tx_state('a'))
        self.assertEqual('tx_dir/state/0000000001',   c.tx_state(1))
        self.assertEqual('tx_dir/journal/',           c.journal())
        self.assertEqual('tx_dir/journal/a',          c.journal('a'))
        self.assertEqual('tx_dir/journal/0000000001', c.journal(1))
        self.assertEqual('tx_dir/txidset',            c.txidset())
        self.assertEqual('tx_dir/txid_maker',         c.txid_maker())
        self.assertEqual('seq_dir/',                  c.seq())
        self.assertEqual('seq_dir/a',                 c.seq('a'))

        self.assertEqual(zkutil.make_kazoo_digest_acl((('foo', 'bar', 'cd'), ('xp', '123', 'cdrwa'))),
                         c.kazoo_digest_acl())
        self.assertEqual(('digest', 'a:b'), c.kazoo_auth())

    def test_default(self):
        old = (
            config.zk_hosts,
            config.zk_tx_dir,
            config.zk_record_dir,
            config.zk_lock_dir,
            config.zk_node_id,
            config.zk_auth,
            config.zk_acl,
        )

        config.zk_hosts = 'HOSTS'
        config.zk_tx_dir = 'TX_DIR/'
        config.zk_record_dir = 'RECORD_DIR/'
        config.zk_seq_dir = 'SEQ_DIR/'
        config.zk_lock_dir = 'LOCK_DIR/'
        config.zk_node_id = 'NODE_ID'
        config.zk_auth = ('DIGEST', 'A', 'B')
        config.zk_acl = (('FOO', 'BAR', 'CD'), ('XP', '123', 'CDRWA'))

        c = zkutil.ZKConf()

        self.assertEqual('HOSTS',              c.hosts())
        self.assertEqual('TX_DIR/',            c.tx_dir())
        self.assertEqual('RECORD_DIR/',        c.record_dir())
        self.assertEqual('SEQ_DIR/',           c.seq_dir())
        self.assertEqual('LOCK_DIR/',          c.lock_dir())
        self.assertEqual('NODE_ID',            c.node_id())
        self.assertEqual(('DIGEST', 'A', 'B'), c.auth())

        self.assertEqual((('FOO', 'BAR', 'CD'),
                          ('XP', '123', 'CDRWA')),
                         c.acl())

        self.assertEqual('LOCK_DIR/',                 c.lock())
        self.assertEqual('LOCK_DIR/a',                c.lock('a'))
        self.assertEqual('RECORD_DIR/',               c.record())
        self.assertEqual('RECORD_DIR/a',              c.record('a'))
        self.assertEqual('SEQ_DIR/',                  c.seq())
        self.assertEqual('SEQ_DIR/a',                 c.seq('a'))
        self.assertEqual('TX_DIR/alive/',             c.tx_alive())
        self.assertEqual('TX_DIR/alive/a',            c.tx_alive('a'))
        self.assertEqual('TX_DIR/alive/0000000001',   c.tx_alive(1))
        self.assertEqual('TX_DIR/state/',             c.tx_state())
        self.assertEqual('TX_DIR/state/a',            c.tx_state('a'))
        self.assertEqual('TX_DIR/state/0000000001',   c.tx_state(1))
        self.assertEqual('TX_DIR/journal/',           c.journal())
        self.assertEqual('TX_DIR/journal/a',          c.journal('a'))
        self.assertEqual('TX_DIR/journal/0000000001', c.journal(1))
        self.assertEqual('TX_DIR/txidset',            c.txidset())
        self.assertEqual('TX_DIR/txid_maker',         c.txid_maker())

        self.assertEqual(zkutil.make_kazoo_digest_acl((('FOO', 'BAR', 'CD'), ('XP', '123', 'CDRWA'))),
                         c.kazoo_digest_acl())
        self.assertEqual(('DIGEST', 'A:B'), c.kazoo_auth())

        (
            config.zk_hosts,
            config.zk_tx_dir,
            config.zk_record_dir,
            config.zk_lock_dir,
            config.zk_node_id,
            config.zk_auth,
            config.zk_acl,
        ) = old
