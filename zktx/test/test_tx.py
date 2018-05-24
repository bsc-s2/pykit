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
from pykit.zktx import TXError
from pykit.zktx import TXTimeout
from pykit.zktx import UserAborted
from pykit.zktx import ZKTransaction
from pykit.zktx.test import base

dd = ututil.dd

zkhost = '127.0.0.1:2181'


class TestTX(base.ZKTestBase):

    def setUp(self):
        super(TestTX, self).setUp()

        self.zk.create('tx', 'tx')
        self.zk.create('lock', '{}')
        self.zk.create('tx/txidset', '{}')
        self.zk.create('tx/alive', '{}')
        self.zk.create('tx/txid_maker', '{}')
        self.zk.create('tx/journal', '{}')
        self.zk.create('record', '{}')

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
            self.assertEqual(None, f2.v)
            f2.v = 2
            t1.set(f2)

            t1.commit()

        rst, ver = self.zk.get('record/foo')
        self.assertEqual([[-1, None], [1, 2]], utfjson.load(rst))

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

    def test_redo_dead_tx_with_journal(self):

        t1 = ZKTransaction(zkhost)
        t1.begin()
        t1.lock_get('foo')
        # fake a half-unlocked condition: bar is released but not foo
        t1.zkstorage.journal.create(t1.txid, {'foo': 555, 'bar': 666})

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
        self.assertEqual(556, rst[-1][1])

        rst, ver = t.zkstorage.record.get('bar')
        dd(rst)
        self.assertEqual(666, rst[-1][1])

        rst, ver = t.zkstorage.txidset.get()
        dd(rst)
        self.assertEqual([1, 3], rst[COMMITTED][0])

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
