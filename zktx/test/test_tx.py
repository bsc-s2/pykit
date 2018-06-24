#!/usr/bin/env python
# coding: utf-8

import time

from pykit import rangeset
from pykit import threadutil
from pykit import utfjson
from pykit import ututil
from pykit import zktx
from pykit.zktx import ABORTED
from pykit.zktx import COMMITTED
from pykit.zktx import PURGED
from pykit.zktx import ConnectionLoss
from pykit.zktx import Deadlock
from pykit.zktx import HigherTXApplied
from pykit.zktx import NotLocked
from pykit.zktx import TXError
from pykit.zktx import TXTimeout
from pykit.zktx import UnlockNotAllowed
from pykit.zktx import UserAborted
from pykit.zktx import ZKTransaction
from pykit.zktx.test import base

dd = ututil.dd

zkhost = '127.0.0.1:2181'


class TXBase(base.ZKTestBase):

    def setUp(self):
        super(TXBase, self).setUp()

        self.zk.create('tx', 'tx')
        self.zk.create('lock', '{}')
        self.zk.create('tx/txidset', '{}')
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
        self.assertEqual([[-1, None], [1, 1]], utfjson.load(rst))

        rst, ver = self.zk.get('tx/txidset')
        self.assertEqual({COMMITTED: [[1, 2]],
                          ABORTED: [],
                          PURGED: [],
                          }, utfjson.load(rst))

    def test_deref(self):

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
        self.assertEqual([[-1, None], [1, {'foo': 'foo'}], [2, {'foo': 'bar'}]],
                         utfjson.load(rst))

    def test_with_statement(self):

        with ZKTransaction(zkhost) as t1:

            foo = t1.lock_get('foo')
            foo.v = 1

            t1.set(foo)

            t1.commit()

        rst, ver = self.zk.get('record/foo')
        self.assertEqual([[-1, None], [1, 1]], utfjson.load(rst))

        rst, ver = self.zk.get('tx/txidset')
        self.assertEqual({COMMITTED: [[1, 2]],
                          ABORTED: [],
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
        self.assertEqual([[-1, None], [1, 2]], utfjson.load(rst))

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
        self.assertEqual([[-1, None], [1, 1]], utfjson.load(rst))

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
        self.assertEqual([[-1, None], [1, 1]], utfjson.load(rst))

    def test_noblocking_lock_get(self):

        with ZKTransaction(zkhost) as t1:

            t1.lock_get('foo')
            f2 = t1.lock_get('foo', blocking=False)
            self.assertIsNotNone(f2)

            with ZKTransaction(zkhost) as t2:

                f4 = t2.lock_get('foo', blocking=False)
                self.assertIsNone(f4)

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
        self.assertEqual(100, rst[-1][1])

        rst, ver = self.zk.get('tx/txidset')
        self.assertEqual({COMMITTED: [[1, 2]],
                          ABORTED: [],
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

        errs = [HigherTXApplied, Deadlock, None]

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
        # 2 error tried and one commit
        self.assertEqual((COMMITTED, 3), (status, txid))

        t = ZKTransaction(zkhost)
        rst, ver = t.zkstorage.record.get('foo')
        self.assertEqual(100, rst[-1][1])

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
        self.assertEqual(100, rst[-1][1])

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
        self.assertEqual(n_tx, rst[-1][1])

        rst, ver = t.zkstorage.txidset.get()
        dd(rst)
        self.assertEqual(n_tx, rst[COMMITTED].length())

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

                except (Deadlock,
                        HigherTXApplied) as e:
                    dd(repr(e))
                    continue

        for th in [threadutil.start_daemon(_tx)
                   for i in range(n_tx)]:

            th.join()

        t = ZKTransaction(zkhost)

        rst, ver = t.zkstorage.record.get('foo')
        dd(rst)
        self.assertEqual(n_tx, rst[-1][1])

        rst, ver = t.zkstorage.txidset.get()
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

                except (Deadlock,
                        HigherTXApplied) as e:
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
            self.assertEqual(n_tx, rst[-1][1])

        rst, ver = t.zkstorage.txidset.get()
        dd(rst)
        self.assertEqual(n_tx, rst[COMMITTED].length())

        # check aborted txidset
        sm = rangeset.union(rst[COMMITTED], rst[ABORTED])
        self.assertEqual(rst[COMMITTED][-1][-1] - 1, sm.length())

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
        self.assertEqual(1, rst[-1][1])

        rst, ver = t.zkstorage.txidset.get()
        dd(rst)
        self.assertEqual([1, 2], rst[ABORTED][0])
        self.assertEqual([2, 3], rst[COMMITTED][0])

    def test_abort(self):

        with ZKTransaction(zkhost) as t1:
            foo = t1.lock_get('foo')
            foo.v = 100
            t1.set(foo)
            t1.abort()

        t = ZKTransaction(zkhost)

        rst, ver = t.zkstorage.record.get('foo')
        dd(rst)
        self.assertEqual(None, rst[-1][1])

        rst, ver = t.zkstorage.txidset.get()
        dd(rst)
        self.assertEqual([1, 2], rst[ABORTED][0])


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

        with ZKTransaction(zkhost) as t1:

            txid = t1.txid
            t1.set_state('bar')

            val, ver = t.zkstorage.state.get(txid)
            self.assertEqual({'got_keys': [], 'data': 'bar'}, val)

            t1.abort()

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
            t1.lock_get('foo')
            t1.set_state('bar')

        with ZKTransaction(zkhost, txid=txid, timeout=0.5) as t2:
            st = t2.get_state()
            self.assertEqual('bar', st)

            try:
                with ZKTransaction(zkhost, txid=txid, timeout=0.5) as t3:
                    dd(t3)
                self.fail("expected TXTimeout")
            except TXTimeout:
                pass

    def test_redo_all(self):

        # txid=1 committed
        # txid=2 nothing
        # txid=3 has journal
        # txid=4 no tx but has state
        # txid=5 committed

        # txid=1
        with ZKTransaction(zkhost) as t1:
            foo = t1.lock_get('foo')
            foo.v = 1
            t1.set(foo)
            t1.commit()

        t = ZKTransaction(zkhost)

        # make txid=2, leave it a hole
        t.zke.set(t.zke._zkconf.txid_maker(), 'x')

        # make txid=3
        t.zke.set(t.zke._zkconf.txid_maker(), 'x')
        txid = 3
        # fake a journal
        t.zkstorage.journal.create(txid, {'bar': 3})

        # txid=4, has state
        t.zke.set(t.zke._zkconf.txid_maker(), 'x')
        t.zkstorage.state.create(4, {'xx': 'yy'})

        # txid=5, committed
        with ZKTransaction(zkhost) as t5:
            foo = t5.lock_get('foo')
            foo.v = 5
            t5.set(foo)
            t5.commit()

        sets, ver = t.zkstorage.txidset.get()
        dd('init txidset:', sets)
        self.assertEqual({'PURGED': [], 'ABORTED': [], 'COMMITTED': [[1, 2], [5, 6]]}, sets)

        t.redo_all_dead_tx()  # redo txid=2, abort
        sets, ver = t.zkstorage.txidset.get()
        dd('after redo 2:', sets)
        self.assertEqual({'PURGED': [], 'ABORTED': [[2, 3]], 'COMMITTED': [[1, 2], [5, 6]]}, sets)

        t.redo_all_dead_tx()  # redo txid=3, committed
        sets, ver = t.zkstorage.txidset.get()
        dd('after redo 3:', sets)
        self.assertEqual({'PURGED': [], 'ABORTED': [[2, 3]], 'COMMITTED': [[1, 2], [3, 4], [5, 6]]}, sets)

        t.redo_all_dead_tx()  # redo txid=4, can not redo a tx with state
        sets, ver = t.zkstorage.txidset.get()
        dd('after redo 4, ignored 4:', sets)
        self.assertEqual({'PURGED': [], 'ABORTED': [[2, 3]], 'COMMITTED': [[1, 2], [3, 4], [5, 6]]}, sets)

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
