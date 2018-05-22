#!/usr/bin/env python
# coding: utf-8

import logging

from kazoo.exceptions import BadVersionError

from pykit import rangeset
from pykit import utfjson
from pykit import zkutil

from .status import STATUS
from .storage import Storage
from .zkaccessor import ZKKeyValue
from .zkaccessor import ZKValue

logger = logging.getLogger(__name__)


class ZKStorage(Storage):

    conflicterror = BadVersionError

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

    def watch_acquire_key(self, txid, key, timeout):

        logger.info('watch acquire: {txid} {key}'.format(txid=txid, key=key))

        keylock = self._make_key_lock(txid, key)

        for holder, ver in keylock.watch_acquire(timeout=timeout):
            yield int(holder), ver

    def try_release_key(self, txid, key):

        logger.info('releasing: {txid} {key}'.format(txid=txid, key=key))

        keylock = self._make_key_lock(txid, key)

        locked, txid, ver = keylock.try_lock()
        if locked:
            keylock.release()
        else:
            keylock.close()

        return locked, utfjson.load(txid), ver

    def _make_key_lock(self, txid, key):
        keylock = zkutil.ZKLock(key,
                                zkclient=self.zkclient,
                                zkconf=self.zkclient._zkconf,
                                ephemeral=False,
                                identifier=utfjson.dump(txid))

        return keylock


def txidset_load(value):
    rst = {}
    for k in STATUS:
        if k not in value:
            value[k] = []
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
