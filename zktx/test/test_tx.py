#!/usr/bin/env python
# coding: utf-8

import time

from kazoo.exceptions import NoNodeError

from pykit import threadutil
from pykit import utfjson
from pykit import ututil
from pykit import zktx
from pykit import zkutil
from pykit.zktx import COMMITTED
from pykit.zktx import PURGED
from pykit.zktx import ConnectionLoss
from pykit.zktx import Deadlock
from pykit.zktx import NotLocked
from pykit.zktx import TXError
from pykit.zktx import TXTimeout
from pykit.zktx import UnlockNotAllowed
from pykit.zktx import UserAborted
from pykit.zktx import CommitError
from pykit.zktx import ZKTransaction
from pykit.zktx.test import base

dd = ututil.dd

zkhost = '127.0.0.1:21811'


class TXBase(base.ZKTestBase):

    def setUp(self):
        super(TXBase, self).setUp()

        self.zk.create('tx', 'tx')
        self.zk.create('lock', '{}')
        self.zk.create('tx/journal_id_set', '{}')
        self.zk.create('tx/alive', '{}')
        self.zk.create('tx/txid_maker', '{}')
        self.zk.create('tx/journal', '{}')
        self.zk.create('tx/state', '{}')
        self.zk.create('record', '{}')


class TestTX(TXBase):

    def test_single_record(self):

        tx = ZKTransaction(zkhost)
        tx.begin()

        foo = tx.lock_get('foo')
        self.assertEqual('foo', foo.k)
        self.assertIsNone(foo.v)
        foo.v = 1

        tx.set(foo)

        tx.commit()

        rst, ver = self.zk.get('record/foo')
        self.assertEqual([None, 1], utfjson.load(rst))

        rst, ver = self.zk.get('tx/journal_id_set')
        self.assertEqual({COMMITTED: [[0, 1]],
                          PURGED: [],
                          }, utfjson.load(rst))

    def test_deepcopy_value(self):

        with ZKTransaction(zkhost) as t1:

            foo = t1.lock_get('foo')
            foo.v = {'foo': 'foo'}
            t1.set(foo)
            t1.commit()

        with ZKTransaction(zkhost) as t1:

            # When retrieving a dict, it should be deep-copied.
            # All zktx always though modified == original
            foo = t1.lock_get('foo')
            foo.v['foo'] = 'bar'
            t1.set(foo)
            t1.commit()

        rst, ver = self.zk.get('record/foo')
        self.assertEqual([{'foo': 'foo'}, {'foo': 'bar'}],
                         utfjson.load(rst)[-2:])

    def test_empty_commit(self):

        with ZKTransaction(zkhost) as t1:

            foo = t1.lock_get('foo')
            foo.v = {'foo': 'foo'}
            t1.commit()

        rst, ver = self.zk.get('tx/journal_id_set')
        self.assertEqual({}, utfjson.load(rst))

    def test_empty_commit_force(self):

        with ZKTransaction(zkhost) as t1:

            foo = t1.lock_get('foo')
            foo.v = {'foo': 'foo'}
            t1.commit(force=True)

        rst, ver = self.zk.get('tx/journal_id_set')
        self.assertEqual({COMMITTED: [[0, 1]],
                          PURGED: [],
                          }, utfjson.load(rst))

        rst, ver = self.zk.get('tx/journal/journal_id0000000000')
        self.assertEqual({}, utfjson.load(rst))

    def test_with_statement(self):

        with ZKTransaction(zkhost) as t1:

            foo = t1.lock_get('foo')
            foo.v = 1

            t1.set(foo)

            t1.commit()

        rst, ver = self.zk.get('record/foo')
        self.assertEqual([None, 1], utfjson.load(rst))

        rst, ver = self.zk.get('tx/journal_id_set')
        self.assertEqual({COMMITTED: [[0, 1]],
                          PURGED: [],
                          }, utfjson.load(rst))

    def test_lock_get_twice(self):

        with ZKTransaction(zkhost) as t1:

            foo = t1.lock_get('foo')
            foo.v = 1
            t1.set(foo)

            f2 = t1.lock_get('foo')
            self.assertEqual(1, f2.v)
            f2.v = 2
            t1.set(f2)

            t1.commit()

        rst, ver = self.zk.get('record/foo')
        self.assertEqual([None, 2], utfjson.load(rst))

    def test_lock_get_latest(self):

        with ZKTransaction(zkhost) as t1:

            foo = t1.lock_get('foo')
            self.assertEqual(None, foo.v)

            foo.v = 1

            # lock_get retrieves original value without set
            f1 = t1.lock_get('foo')
            self.assertEqual(None, f1.v)

            t1.set(foo)

            # lock_get can retrieve latest value after set
            f2 = t1.lock_get('foo')
            self.assertEqual(1, f2.v)

            t1.commit()

        rst, ver = self.zk.get('record/foo')
        self.assertEqual([None, 1], utfjson.load(rst))

    def test_lock_get_not_latest(self):

        with ZKTransaction(zkhost) as t1:

            foo = t1.lock_get('foo')
            foo.v = 1
            t1.set(foo)

            # lock_get retrieves original value when latest is False
            f2 = t1.lock_get('foo', latest=False)
            self.assertEqual(None, f2.v)

            t1.commit()

        rst, ver = self.zk.get('record/foo')
        self.assertEqual([None, 1], utfjson.load(rst))

    def test_noblocking_lock_get(self):

        with ZKTransaction(zkhost) as t1:

            t1.lock_get('foo')
            f2 = t1.lock_get('foo', blocking=False)
            self.assertIsNotNone(f2)

            with ZKTransaction(zkhost) as t2:

                f4 = t2.lock_get('foo', blocking=False)
                self.assertIsNone(f4)

        t = ZKTransaction(zkhost)
        t.begin()
        t.lock_get('foo')
        t.zke.stop()

        dd(self.zk.get('lock/foo'))
        # can lock the key which is hold by a dead tx without state
        with ZKTransaction(zkhost) as t1:
            self.assertIsNotNone(t1.lock_get('foo', blocking=False))

        t = ZKTransaction(zkhost)
        t.begin()
        t.lock_get('foo')
        t.set_state('s')
        t.zke.stop()

        dd(self.zk.get('lock/foo'))
        # can not lock the key which is hold by a dead tx with state
        with ZKTransaction(zkhost) as t1:
            self.assertIsNone(t1.lock_get('foo', blocking=False))

    def test_lock_get_timeout(self):

        def _tx(tx):
            tx.begin()
            tx.lock_get('foo')
            time.sleep(4)

        th = threadutil.start_daemon(_tx, args=(ZKTransaction(zkhost, txid=0),))

        with ZKTransaction(zkhost, lock_timeout=0.5) as t1:

            try:
                t1.lock_get('foo')
                self.fail('TXTimeout expected')
            except TXTimeout as e:
                dd(repr(e))

        with ZKTransaction(zkhost) as t2:

            try:
                t2.lock_get('foo', timeout=0.5)
                self.fail('TXTimeout expected')
            except TXTimeout as e:
                dd(repr(e))

        th.join()

    def test_unlock(self):

        with ZKTransaction(zkhost) as t1:

            foo = t1.lock_get('foo')
            t1.unlock(foo)

            self.assertEqual({}, t1.got_keys)

            # re-get is ok
            foo = t1.lock_get('foo')
            t1.unlock(foo)

            with ZKTransaction(zkhost) as t2:
                # t2 can lock a unlocked key
                t2.lock_get('foo')

    def test_unlock_nonlocked(self):

        with ZKTransaction(zkhost) as t1:

            foo = t1.lock_get('foo')
            t1.unlock(foo)
            self.assertRaises(NotLocked, t1.unlock, foo)

    def test_unlock_changed_record(self):

        with ZKTransaction(zkhost) as t1:

            foo = t1.lock_get('foo')
            t1.set(foo)
            self.assertRaises(UnlockNotAllowed, t1.unlock, foo)

    def test_run_tx(self):

        def _tx(tx):
            foo = tx.lock_get('foo')
            foo.v = 100
            tx.set(foo)
            tx.commit()

        status, txid = zktx.run_tx(zkhost, _tx)
        self.assertEqual((COMMITTED, 1), (status, txid))

        t = ZKTransaction(zkhost)
        rst, ver = t.zkstorage.record.get('foo')
        self.assertEqual(100, rst[-1])

        rst, ver = self.zk.get('tx/journal_id_set')
        self.assertEqual({COMMITTED: [[0, 1]],
                          PURGED: [],
                          }, utfjson.load(rst))

    def test_run_tx_timeout(self):

        def _tx(tx):
            tx.lock_get('foo')
            time.sleep(0.5)
            tx.commit()

        try:
            zktx.run_tx(zkhost, _tx, timeout=0.4)
            self.fail('TXTimeout expected')
        except TXTimeout as e:
            dd(repr(e))

    def test_run_tx_lock_timeout(self):

        def _tx0(tx):
            tx.begin()
            tx.lock_get('foo')
            time.sleep(2)

        def _tx1(tx):
            tx.lock_get('foo')
            time.sleep(0.2)
            tx.commit()

        th = threadutil.start_daemon(_tx0, args=(ZKTransaction(zkhost, txid=0),))

        try:
            zktx.run_tx(zkhost, _tx1, lock_timeout=0.4)
            self.fail('TXTimeout expected')
        except TXTimeout as e:
            dd(repr(e))

        th.join()

    def test_run_tx_conn_loss(self):

        def _tx(tx):
            tx.lock_get('foo')
            tx.zke.stop()
            tx.commit()

        try:
            zktx.run_tx(zkhost, _tx)
            self.fail('ConnectionLoss expected')
        except ConnectionLoss as e:
            dd(repr(e))

    def test_run_tx_retriable_error(self):

        errs = [Deadlock, None]

        def _tx(tx):

            foo = tx.lock_get('foo')
            foo.v = 100
            tx.set(foo)

            err = errs.pop(0)
            if err is not None:
                raise err()
            else:
                tx.commit()

        status, txid = zktx.run_tx(zkhost, _tx)
        # 1 error tried and one commit
        self.assertEqual((COMMITTED, 2), (status, txid))

        t = ZKTransaction(zkhost)
        rst, ver = t.zkstorage.record.get('foo')
        self.assertEqual(100, rst[-1])

    def test_run_tx_unretriable_error(self):

        sess = dict(n=0)
        errs = [UserAborted, TXTimeout, ConnectionLoss, None]

        def _tx(tx, err):

            sess['n'] += 1

            foo = tx.lock_get('foo')
            foo.v = 100
            tx.set(foo)

            if err is not None:
                raise err()
            else:
                tx.commit()

        for err in errs:
            try:
                zktx.run_tx(zkhost, _tx, args=(err, ))
            except TXError as e:
                dd(repr(e))

        self.assertEqual(len(errs), sess['n'])

        tx = ZKTransaction(zkhost)
        rst, ver = tx.zkstorage.record.get('foo')
        self.assertEqual(100, rst[-1])

    def test_sequential(self):

        n_tx = 10
        k = 'foo'

        for ii in range(n_tx):

            with ZKTransaction(zkhost) as t1:

                foo = t1.lock_get(k)
                foo.v = foo.v or 0
                foo.v += 1

                t1.set(foo)

                t1.commit()

        t = ZKTransaction(zkhost)

        rst, ver = t.zkstorage.record.get(k)
        dd(rst)
        self.assertEqual(n_tx, rst[-1])

        rst, ver = t.zkstorage.journal_id_set.get()
        dd(rst)
        self.assertEqual(n_tx, rst[COMMITTED].length())

    def test_journal_purge(self):

        n_tx = 10
        k = 'foo'

        for ii in range(n_tx):

            with ZKTransaction(zkhost) as t1:
                t1.zkstorage.max_journal_history = 5
                foo = t1.lock_get(k)
                foo.v = foo.v or 0
                foo.v += 1
                t1.set(foo)
                t1.commit()

        t = ZKTransaction(zkhost)
        journal_id_set, ver = t.zkstorage.journal_id_set.get()
        self.assertEqual({PURGED: [[0, 5]], COMMITTED: [[0, 10]]}, journal_id_set)

        for i in range(5):
            self.assertRaises(NoNodeError, t.zkstorage.journal.get, i)

    def test_concurrent_single_record(self):

        n_tx = 10

        def _tx():
            while True:
                try:
                    with ZKTransaction(zkhost) as t1:

                        foo = t1.lock_get('foo')
                        foo.v = foo.v or 0
                        foo.v += 1

                        t1.set(foo)
                        t1.commit()
                        return

                except Deadlock as e:
                    dd(repr(e))
                    continue

        for th in [threadutil.start_daemon(_tx)
                   for i in range(n_tx)]:

            th.join()

        t = ZKTransaction(zkhost)

        rst, ver = t.zkstorage.record.get('foo')
        dd(rst)
        self.assertEqual(n_tx, rst[-1])

        rst, ver = t.zkstorage.journal_id_set.get()
        dd(rst)
        self.assertEqual(n_tx, rst[COMMITTED].length())

    def test_concurrent_3_record(self):

        n_tx = 10
        ks = ('foo', 'bar', 'duu')

        def _tx(i):
            while True:
                try:
                    with ZKTransaction(zkhost) as t1:

                        for ii in range(len(ks)):
                            k = ks[(ii+i) % len(ks)]

                            foo = t1.lock_get(k)
                            foo.v = foo.v or 0
                            foo.v += 1

                            t1.set(foo)

                        t1.commit()
                        dd(str(t1) + ' committed')
                        return

                except Deadlock as e:
                    dd(str(t1) + ': ' + repr(e))
                    continue
                except TXTimeout as e:
                    dd(str(t1) + ': ' + repr(e))
                    raise

        with ututil.Timer() as tt:

            for th in [threadutil.start_daemon(_tx, args=(i, ))
                       for i in range(n_tx)]:

                th.join()

            dd('3 key 10 thread: ', tt.spent())

        t = ZKTransaction(zkhost)

        for k in ks:
            rst, ver = t.zkstorage.record.get(k)
            dd(rst)
            self.assertEqual(n_tx, rst[-1])

        rst, ver = t.zkstorage.journal_id_set.get()
        dd(rst)
        self.assertEqual(n_tx, rst[COMMITTED].length())

    def test_redo_dead_tx_without_journal(self):

        t1 = ZKTransaction(zkhost)
        t1.begin()
        t1.lock_get('foo')

        t1.zke.stop()

        with ZKTransaction(zkhost) as t2:

            foo = t2.lock_get('foo')
            foo.v = foo.v or 0
            foo.v += 1

            t2.set(foo)
            t2.commit()

        t = ZKTransaction(zkhost)

        rst, ver = t.zkstorage.record.get('foo')
        dd(rst)
        self.assertEqual(1, rst[-1])

        journal_id_set, ver = t.zkstorage.journal_id_set.get()
        self.assertEqual({COMMITTED: [[0, 1]], PURGED: []}, journal_id_set)

    def test_abort(self):

        try:
            with ZKTransaction(zkhost) as t1:
                foo = t1.lock_get('foo')
                foo.v = 100
                t1.set(foo)
                t1.abort()
        except UserAborted:
            pass

        t = ZKTransaction(zkhost)

        rst, ver = t.zkstorage.record.get('foo')
        dd(rst)
        self.assertEqual(None, rst[-1])

    def test_delete_node(self):
        k = 'foo'
        with ZKTransaction(zkhost) as t1:
            foo = t1.lock_get(k)
            foo.v = 'foo'
            t1.set(foo)
            t1.commit()

        t = ZKTransaction(zkhost)
        self.assertEqual(([None, 'foo'], 0), t.zkstorage.record.get('foo'))

        with ZKTransaction(zkhost) as t1:
            foo = t1.lock_get(k)
            foo.v = None
            t1.set(foo)
            t1.commit()

        self.assertEqual(([None], -1), t.zkstorage.record.get('foo'))
        self.assertRaises(NoNodeError, t.zkstorage.zke.get, 'foo')

    def test_commit_error(self):
        k = 'foo'
        with ZKTransaction(zkhost) as t1:
            foo = t1.lock_get(k)
            foo.v = 'foo'
            t1.set(foo)
            t1.commit()

        try:
            with ZKTransaction(zkhost) as t1:
                foo = t1.lock_get(k)
                foo.v = 'ex'
                t1.got_keys[k].version = 100
                t1.set(foo)
                t1.commit()

            self.fail('not raise commit error')

        except CommitError:
            pass

    def test_acl(self):
        k = 'tacl'
        with ZKTransaction(self.zkauthed) as t1:
            foo = t1.lock_get(k)
            foo.v = 'foo'
            t1.set(foo)
            t1.commit()

            acls, _ = self.zk.get_acls(self.zkauthed._zkconf.record(k))
            self.assertEqual(self.zkauthed._zkconf.kazoo_digest_acl(), acls)

            acls, _ = self.zk.get_acls(self.zkauthed._zkconf.journal(0))
            self.assertEqual(self.zkauthed._zkconf.kazoo_digest_acl(), acls)


class TestTXState(TXBase):

    def test_committed(self):

        t = ZKTransaction(zkhost)
        txid = None

        with ZKTransaction(zkhost) as t1:

            txid = t1.txid

            # not set yet
            self.assertIsNone(t.zkstorage.state.get(txid)[0])

            foo = t1.lock_get('foo')
            foo.v = 100
            t1.set(foo)
            t1.set_state('bar')

            val, ver = t.zkstorage.state.get(txid)
            self.assertEqual({'got_keys': ['foo'], 'data': 'bar'}, val)

            t1.commit()

        self.assertIsNone(t.zkstorage.state.get(txid)[0])

    def test_user_abort(self):

        t = ZKTransaction(zkhost)
        txid = None

        try:
            with ZKTransaction(zkhost) as t1:

                txid = t1.txid
                t1.set_state('bar')

                val, ver = t.zkstorage.state.get(txid)
                self.assertEqual({'got_keys': [], 'data': 'bar'}, val)

                t1.abort()
        except UserAborted:
            pass

        self.assertIsNone(t.zkstorage.state.get(txid)[0])

    def test_exception(self):

        # tx raised by other exception is recoverable

        t = ZKTransaction(zkhost)
        txid = None

        try:
            with ZKTransaction(zkhost) as t1:

                txid = t1.txid
                t1.set_state('bar')

                val, ver = t.zkstorage.state.get(txid)
                self.assertEqual({'got_keys': [], 'data': 'bar'}, val)

                raise ValueError('foo')

        except ValueError:
            pass

        val, ver = t.zkstorage.state.get(txid)
        self.assertEqual({'got_keys': [], 'data': 'bar'}, val)

    def test_exception_and_recover(self):

        # tx raised by other exception is recoverable

        t = ZKTransaction(zkhost)
        txid = None

        try:
            with ZKTransaction(zkhost) as t1:

                txid = t1.txid

                f1 = t1.lock_get('foox')
                f1.v = "foox_val"
                t1.set(f1)

                t1.set_state('bar')

                val, ver = t.zkstorage.state.get(txid)
                self.assertEqual({'got_keys': ["foox"], 'data': 'bar'}, val)

                raise ValueError('foo')

        except ValueError:
            pass

        val, ver = t.zkstorage.state.get(txid)
        self.assertEqual({'got_keys': ['foox'], 'data': 'bar'}, val)

        ident = zkutil.make_identifier(txid, None)
        keylock = zkutil.ZKLock('foox',
                                zkclient=t.zke,
                                zkconf=t.zke._zkconf,
                                ephemeral=False,
                                identifier=ident)

        val, ver = keylock.get_lock_val()
        self.assertEqual(val['v'], "foox_val")

        with ZKTransaction(zkhost, txid=txid, timeout=1) as t1:
            f1 = t1.lock_get('foox')
            self.assertEqual(f1.v, "foox_val")

            val = t1.get_state()
            self.assertEqual(val, 'bar')

    def test_timeout(self):

        # timeout on waiting is recoverable

        t = ZKTransaction(zkhost)
        txid = None

        try:
            with ZKTransaction(zkhost, timeout=0.5) as t1:

                txid = t1.txid

                # t.txid is higher
                t.begin()
                t.lock_get('foo')

                t1.set_state('bar')
                t1.lock_get('foo')  # should timeout waiting for higher txid

        except TXTimeout:
            pass

        val, ver = t.zkstorage.state.get(txid)
        self.assertEqual({'got_keys': [], 'data': 'bar'}, val)

    def test_deadlock(self):

        # deadlock is not recoverable

        t = ZKTransaction(zkhost)
        # t.txid is lower
        t.begin()
        t.lock_get('foo')

        def _commit():
            t.commit()

        txid = None

        try:
            with ZKTransaction(zkhost, timeout=0.5) as t1:

                txid = t1.txid

                # lock another key first to produce deadlock
                t1.lock_get('woo')

                t1.set_state('bar')
                threadutil.start_daemon(_commit, after=0.2)
                t1.lock_get('foo')  # should deadlock waiting for higher txid

        except Deadlock:
            pass

        t = ZKTransaction(zkhost)
        self.assertIsNone(t.zkstorage.state.get(txid)[0])

    def test_uncommitted(self):

        # uncommitted is recoverable

        t = ZKTransaction(zkhost)
        txid = None

        with ZKTransaction(zkhost, timeout=0.5) as t1:

            txid = t1.txid
            t1.lock_get('foo')
            t1.set_state('bar')

        val, ver = t.zkstorage.state.get(txid)
        self.assertEqual({'got_keys': ['foo'], 'data': 'bar'}, val)

    def test_list_recoverable(self):

        txid = None
        with ZKTransaction(zkhost, timeout=0.5) as t1:

            txid = t1.txid
            t1.lock_get('foo')
            t1.set_state('bar')

            with ZKTransaction(zkhost, timeout=0.5) as t2:
                txid = t2.txid
                t2.lock_get('foo2')
                t2.set_state('bar2')

            self.assertEqual([(txid, 'bar2')],
                             [x for x in zktx.list_recoverable(zkhost)])

    def test_recover(self):

        txid = None
        with ZKTransaction(zkhost, timeout=0.5) as t1:

            txid = t1.txid
            f1 = t1.lock_get('foo')
            f2 = t1.lock_get('foo2')

            f1.v = "foo_val"
            f2.v = "foo2_val"

            t1.set(f1)
            t1.set(f2)

            t1.set_state('bar')

        with ZKTransaction(zkhost, txid=txid, timeout=0.5) as t2:
            st = t2.get_state()
            self.assertEqual('bar', st)

            f1 = t2.lock_get('foo')
            f2 = t2.lock_get('foo2')

            self.assertEqual(f1.v, "foo_val")
            self.assertEqual(f2.v, "foo2_val")

            try:
                with ZKTransaction(zkhost, txid=txid, timeout=0.5) as t3:
                    dd(t3)
                self.fail("expected TXTimeout")
            except TXTimeout:
                pass

    def test_unlock_with_state(self):

        # NotLocked is retrieable

        txid = None

        try:
            with ZKTransaction(zkhost, timeout=0.5) as t1:

                txid = t1.txid
                t1.set_state('bar')

                foo = t1.lock_get('foo')
                t1.unlock(foo)
                t1.unlock(foo)

        except NotLocked:
            pass

        t = ZKTransaction(zkhost)
        val, ver = t.zkstorage.state.get(txid)
        self.assertEqual({'got_keys': [], 'data': 'bar'}, val)

        # UnlockNotAllowed is retrieable

        txid = None

        try:
            with ZKTransaction(zkhost, timeout=0.5) as t1:

                txid = t1.txid
                t1.set_state('bar')

                foo = t1.lock_get('foo')
                t1.set(foo)
                t1.unlock(foo)

        except UnlockNotAllowed:
            pass

        t = ZKTransaction(zkhost)
        val, ver = t.zkstorage.state.get(txid)
        self.assertEqual({'got_keys': [], 'data': 'bar'}, val)

    def test_exception_with_state(self):

        t = ZKTransaction(zkhost)
        txid = None

        try:
            with ZKTransaction(zkhost) as t1:
                t1.lock_get('foo')
                raise ValueError('foo')
        except ValueError:
            pass

        nodes = t.zke.get_children('/lock')
        self.assertEqual([], nodes)

        try:
            with ZKTransaction(zkhost) as t2:
                txid = t2.txid
                t2.lock_get('foo')
                t2.set_state('bar')
                raise ValueError('foo')
        except ValueError:
            pass

        val, ver = t.zkstorage.state.get(txid)
        self.assertEqual({'got_keys': ['foo'], 'data': 'bar'}, val)

        nodes = t.zke.get_children('/lock')
        self.assertEqual(['foo'], nodes)

    def test_txid_in_run_tx(self):

        txids = []
        count = iter([1, 2, 3])

        def _tx_func(tx):
            for i in count:
                txids.append(tx.txid)
                if i != 3:
                    raise Deadlock()

        zktx.run_tx(zkhost, _tx_func, txid=5)
        dd(txids)

        self.assertEqual(5, txids[0])

        for i in txids[1:]:
            self.assertNotEqual(5, i)
