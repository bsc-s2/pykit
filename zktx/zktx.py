#!/usr/bin/env python
# coding: utf-8

import copy
import logging
import threading
import time

from kazoo import exceptions
from kazoo.client import KazooState
from kazoo.exceptions import KazooException
from kazoo.exceptions import NoNodeError

from pykit import rangeset
from pykit import zkutil

from .exceptions import ConnectionLoss
from .exceptions import Deadlock
from .exceptions import HigherTXApplied
from .exceptions import RetriableError
from .exceptions import TXTimeout
from .exceptions import UserAborted
from .status import ABORTED
from .status import COMMITTED
from .zkstorage import ZKStorage

logger = logging.getLogger(__name__)


class TXRecord(object):

    def __init__(self, k, v, txid):
        self.k = k
        self.v = v
        self.txid = txid

    def __str__(self):
        return '{k}={v}@{txid}'.format(
            k=self.k, v=self.v, txid=txidstr(self.txid))


class ZKTransaction(object):

    def __init__(self, zk, timeout=None):

        if timeout is None:
            timeout = 10

        # Save the original arg for self.run()
        self._zk = zk

        self.zke, self.owning_zk = zkutil.kazoo_client_ext(zk)
        self.timeout = timeout

        self.txid = None
        self.expire_at = None
        self.tx_alive_lock = None

        # User locked and required keys
        self.got_keys = {}
        # Keys user need to commit
        self.modifications = {}

        self.state_lock = threading.RLock()
        self.connected = True

        self.tx_status = None

        self.zkstorage = ZKStorage(self.zke)

        self.zke.add_listener(self._on_conn_change)

    def _on_conn_change(self, state):

        logger.debug('state changed: {state}'.format(state=state,))

        with self.state_lock:
            if state == KazooState.LOST or state == KazooState.SUSPENDED:
                self.connected = False

    def lock_get(self, key):

        # We use persistent lock(ephemeral=False)
        # thus we do not need to care about connection loss during locking
        # phase.
        # But we still need to check connection when creating journal.

        if key in self.got_keys:
            return copy.deepcopy(self.got_keys[key])

        self.lock_key(key)

        val, version = self.zkstorage.record.get(key)
        ltxid, lvalue = val[-1]

        curr = TXRecord(k=key, v=lvalue, txid=ltxid)
        self.got_keys[key] = curr

        if ltxid > self.txid:
            raise HigherTXApplied('{tx} seen a higher txid applied: {txid}'.format(
                tx=self, txid=ltxid))

        rec = TXRecord(k=key, v=lvalue, txid=ltxid)
        return rec

    def set(self, rec):
        logger.info('{tx} tx.set: {rec}'.format(tx=self, rec=rec))
        self.modifications[rec.k] = rec

    def lock_key(self, key):

        try:
            for other_txid, ver in self.zkstorage.acquire_key_loop(
                    self.txid, key, timeout=self.time_left()):

                logger.info('{tx} wait[{key}]-> {other_txid} ver: {ver}'.format(
                    tx=self, key=key, other_txid=txidstr(other_txid), ver=ver))

                if not self.is_tx_alive(other_txid):
                    rst = self.redo_dead_tx(other_txid)

                    # aborted tx did not release lock by itself
                    if rst == ABORTED:
                        self.zkstorage.try_release_key(other_txid, key)

                    continue

                logger.info('{tx}: other tx {other_txid} is alive'.format(
                    tx=self, other_txid=txidstr(other_txid)))

                if self.txid > other_txid:

                    if len(self.got_keys) == 0:

                        # no locking, no deadlock
                        logger.info('{tx} wait[{key}]-> {other_txid} no-lock'.format(
                            tx=self, key=key, other_txid=txidstr(other_txid)))

                        for i in range(other_txid, self.txid):
                            self.wait_tx_to_finish(i)
                        continue
                    else:
                        # let earlier tx to finish first
                        logger.info('{tx} wait[{key}]-> {other_txid} deadlock'.format(
                            tx=self, key=key, other_txid=txidstr(other_txid)))

                        self.release_all_key_locks()
                        for i in range(other_txid, self.txid):
                            self.wait_tx_to_finish(i)

                        raise Deadlock('my txid: {mytxid} lockholder txid: {other_txid}'.format(
                            mytxid=self.txid, other_txid=other_txid))

                # self.txid < other_txid:
                # I am an earlier tx. I should run first.
                #
                # If there is no deadlock:
                #   the older tx will finish later. Then I wait.
                #
                # If there is a deadlock:
                #   the older tx will abort.
                logger.info('{tx} wait[{key}]-> {other_txid}'.format(
                    tx=self, key=key, other_txid=txidstr(other_txid)))

        except zkutil.LockTimeout:
            raise TXTimeout('{tx} timeout waiting for lock: {key}'.format(tx=self, key=key))

        logger.info('{tx} [{key}] locked'.format(tx=self, key=key))

    def wait_tx_to_finish(self, txid):

        logger.info('{tx} wait-> {other_txid}'.format(tx=self, other_txid=txidstr(txid)))

        try:
            zkutil.wait_absent(self.zke,
                               self.zke._zkconf.tx_alive(txid),
                               timeout=self.time_left())
        except zkutil.ZKWaitTimeout as e:

            logger.info(repr(e) + ' while waiting for other tx: {txid}'.format(
                txid=txid))

            raise TXTimeout('{tx} timeout waiting for tx:{txid}'.format(tx=self, txid=txid))

    def redo_all_dead_tx(self):

        sets = self.zkstorage.txidset.get()

        # Only check for holes in the txid range set.
        # With `txidset = [[1, 2], [4, 5]]`, tx-2 and tx-3 is unfinished tx.
        # Check these tx

        # A tx is committed or aborted that does not need to handle it again.
        known = rangeset.union(sets[COMMITTED], sets[ABORTED])

        for rng in known[:-1]:

            txid = rng[1]

            if not self.is_tx_alive(txid):
                self.redo_dead_tx(txid)

    def redo_dead_tx(self, txid):

        dead_tx = ZKTransaction(self.zke,
                                timeout=self.expire_at - time.time())

        dead_tx.begin(txid=txid)
        rst = dead_tx.redo()
        dead_tx._close()
        return rst

    def redo(self):

        logger.info('REDO: {tx}'.format(tx=self))

        txidset, ver = self.zkstorage.txidset.get()
        logger.info('{tx} got txidset: {txidset}'.format(tx=self, txidset=txidset))

        if txidset[COMMITTED].has(self.txid):
            return COMMITTED
        elif txidset[ABORTED].has(self.txid):
            return ABORTED

        # self.txid is not in txidset

        try:
            jour, version = self.zkstorage.journal.get(self.txid)
        except NoNodeError:
            # This tx has not yet written a journal.
            # Nothing to apply
            self.zkstorage.add_to_txidset(ABORTED, self.txid)
            return ABORTED

        # A tx maybe killed when its key locks are half released.
        #
        # Because unlocking always happens after applying all modifications.
        # Thus applying without locking is ok:
        # Non-locked keys must already have higher or equal txid thus re-apply
        # does not affect.
        for k, v in jour.items():
            self.zkstorage.apply_record(self.txid, k, v)

        # release all key locks
        for key in jour:
            self.zkstorage.try_release_key(self.txid, key)

        self.zkstorage.add_to_txidset(COMMITTED, self.txid)
        return COMMITTED

    def is_tx_alive(self, txid):
        try:
            self.zke.get(self.zke._zkconf.tx_alive(txid))
            logger.info('{tx} tx:{txid} is alive'.format(tx=self, txid=txid))
            return True
        except NoNodeError:
            logger.info('{tx} tx:{txid} is dead'.format(tx=self, txid=txid))
            return False

    def begin(self, txid=None):

        assert self.expire_at is None

        self.expire_at = time.time() + self.timeout

        if txid is not None:
            # Run a specified tx, normally when to recover a dead tx process
            self.txid = txid

        else:
            # Run a new tx, create txid.
            zstat = self.zke.set(self.zke._zkconf.txid_maker(), 'x')
            self.txid = zstat.version

        zkconf = copy.deepcopy(self.zke._zkconf.conf)
        zkconf['lock_dir'] = self.zke._zkconf.tx_alive()

        self.tx_alive_lock = zkutil.ZKLock(self.txid,
                                           zkconf=zkconf,
                                           zkclient=self.zke,
                                           timeout=self.expire_at-time.time())

        self.tx_alive_lock.acquire()

    def commit(self):

        # Only when commit, it is necessary to ensure connection still active:
        # Thus tx_alive_lock is not lost, then no other process would take
        # charge of this tx.

        if self.time_left() < 0:
            raise TXTimeout('{tx} timeout when committing'.format(tx=self))

        self._assert_connected()

        jour = {}

        for k, rec in self.modifications.items():
            curr = self.got_keys[k]
            if rec.v == curr.v:
                continue

            jour[k] = rec.v

        self.zkstorage.journal.create(self.txid, jour)
        logger.info('{tx} written journal: {jour}'.format(
            tx=self, jour=jour))

        for k, v in jour.items():
            self.zkstorage.apply_record(self.txid, k, v)
            logger.info('{tx} applied: {k}={v}'.format(tx=self, k=k, v=v))

        # Must release key locks before add to txidset.
        # A txid presents in txidset means everything is done.
        self.release_all_key_locks()
        self.zkstorage.add_to_txidset(COMMITTED, self.txid)

        logger.info('{tx} updated txidset: {status}'.format(
            tx=self, status=COMMITTED))

        self.tx_status = COMMITTED
        self.modifications = {}
        self._close()

    def abort(self):
        raise UserAborted()

    def is_timeout(self):
        return self.time_left() > 0

    def time_left(self):
        return self.expire_at - time.time()

    def _close(self):

        self.release_all_key_locks()

        if self.tx_alive_lock is not None:

            try:
                self.tx_alive_lock.release()

            except (exceptions.ConnectionClosedError,
                    exceptions.ConnectionLoss) as e:

                logger.warn('{tx} {e} while release tx alive lock'.format(
                    tx=self, e=repr(e)))

            self.tx_alive_lock = None

        self.zke.remove_listener(self._on_conn_change)

        self.modifications = {}

        if self.owning_zk:
            try:
                self.zke.stop()
            except KazooException as e:
                logger.info(repr(e) + ' while zkclient.stop()')

    def release_all_key_locks(self):

        for key in self.got_keys:

            logger.info('{tx} releasing:[{key}]'.format(tx=self, key=key))

            try:
                self.zkstorage.try_release_key(self.txid, key)
            except (exceptions.ConnectionClosedError,
                    exceptions.ConnectionLoss) as e:

                logger.warn('{tx} {e} while release key lock {key}'.format(
                    tx=self, e=repr(e), key=key))
                break

        self.got_keys = {}

    def _assert_connected(self):
        with self.state_lock:
            if not self.connected:
                raise ConnectionLoss()

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, errtype, errval, _traceback):

        logger.info('{tx} __exit__ errtype:{errtype} errval:{errval}'.format(
            tx=self, errtype=errtype, errval=errval))

        try:
            if self.txid is not None and self.tx_status is None:

                self.tx_status = ABORTED
                try:
                    self.zkstorage.add_to_txidset(ABORTED, self.txid)
                except (exceptions.ConnectionClosedError,
                        exceptions.ConnectionLoss) as e:

                    logger.warn('{tx} {e} while adding to txidset.ABORTED'.format(
                        tx=self, e=repr(e)))

            if errval is None:
                return True

            if isinstance(errval, UserAborted):
                return True

            return False

        finally:
            self._close()

    def __str__(self):
        return '{tx}[{locked}]'.format(tx=txidstr(self.txid),
                                       locked=','.join(sorted(self.got_keys.keys())))


def run_tx(zk, func, timeout=None, args=(), kwargs=None):

    if timeout is None:
        timeout = 10

    if kwargs is None:
        kwargs = {}

    expire_at = time.time() + timeout

    while True:

        tx = ZKTransaction(zk, timeout=expire_at - time.time())

        try:
            with tx:
                func(tx, *args, **kwargs)

            assert tx.tx_status is not None, 'with-statement guarantees tx_status is not None'
            return tx.tx_status, tx.txid

        except RetriableError as e:
            logger.info('{tx} {e}'.format(tx=tx, e=repr(e)))
            continue


def txidstr(txid):
    return 'tx-{txid:0>10}'.format(txid=txid)
