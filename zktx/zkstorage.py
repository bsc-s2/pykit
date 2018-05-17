#!/usr/bin/env python
# coding: utf-8

import logging

from pykit import rangeset
from pykit import zkutil

from .storage import Storage
from .zkaccessor import ZKKeyValue
from .zkaccessor import ZKValue

logger = logging.getLogger(__name__)


class ZKStorage(Storage):

    def __init__(self, zkclient):

        assert isinstance(zkclient, zkutil.KazooClientExt)

        self.zkclient = zkclient

        self.txidset = ZKValue(self.zkclient,
                               self.zkclient._zkconf.txidset,
                               load=txidset_load)

        self.journal = ZKKeyValue(self.zkclient,
                                  self.zkclient._zkconf.journal)

        self.record = ZKKeyValue(self.zkclient,
                                 self.zkclient._zkconf.record,
                                 load=record_load,
                                 nonode_callback=record_nonode_cb)

    def try_lock_key(self, txid, key):

        # Use the txid as lock identifier, thus when tx processor recovered,
        # it could re-acquire this lock with no trouble.
        #
        # But we have to guarantee there is only one processor for this tx.
        # And this is done by let the tx processor to acquire a lock named with txid first.

        keylock = None
        try:
            keylock = self._make_key_lock(txid, key)

            locked, txid, ver = keylock.try_lock()
            return locked, txid, ver

        finally:
            if keylock is not None:
                keylock.close()

    def try_release_key(self, txid, key):

        keylock = self._make_key_lock(txid, key)

        locked, txid, ver = keylock.try_lock()
        if locked:
            keylock.release()
        else:
            keylock.close()

        return locked, txid, ver

    def _make_key_lock(self, txid, key):
        keylock = zkutil.ZKLock(key,
                                zkclient=self.zkclient,
                                zkconf=self.zkclient._zkconf,
                                ephemeral=False,
                                identifier=txid)

        return keylock


def txidset_load(value):
    rst = {}
    for k in value:
        rst[k] = rangeset.RangeSet(value[k])
    return rst


def record_load(value):

    # json does not support int as key.
    # It converts int to str.
    # We need to convert it back to int

    rst = {int(k): v
           for k, v in value.items()}
    if len(rst) == 0:
        rst[-1] = None
    return rst


def record_nonode_cb():
    """
    If NoNodeError received, make a default value for a record
    """

    return {-1: None}, -1
