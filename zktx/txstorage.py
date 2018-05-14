#!/usr/bin/env python
# coding: utf-8

import logging

from kazoo.exceptions import NoNodeError

from pykit import rangeset
from pykit import zkutil

from .storage import TXStorageHelper

logger = logging.getLogger(__name__)


class ZKKVAccessor(object):

    def __init__(self, zkclient, get_path, load=None, dump=None, nonode_callback=None):
        self.zkclient = zkclient
        self.get_path = get_path
        self.load = load
        self.dump = dump
        self.nonode_callback = nonode_callback

    def create(self, key, value):
        value = self._dump(value)
        return self.zkclient.create(self.get_path(key), value)

    def delete(self, key, version=None):
        return self.zkclient.delete(self.get_path(key), version=version)

    def set(self, key, value, version=None):
        value = self._dump(value)
        self.zkclient.set(self.get_path(key), value, version=version)

    def get(self, key):
        try:
            val, zstat = self.zkclient.get(self.get_path(key))
            version = zstat.version
        except NoNodeError:
            if self.nonode_callback is not None:
                val, version = self.nonode_callback()
            else:
                raise
        return self._load(val), version

    def _load(self, val):
        if self.load is not None:
            return self.load(val)
        else:
            return val

    def _dump(self, val):
        if self.dump is not None:
            return self.dump(val)
        else:
            return val


class ZKValueAccessor(ZKKVAccessor):

    def __init__(self, zkclient, get_path, load=None, dump=None, nonode_callback=None):

        self.zkclient = zkclient
        self._get_path = get_path
        self.load = load
        self.dump = dump
        self.nonode_callback = nonode_callback

    # super.get_path requires 1 argument.
    # override it and proxy it to our no-argument _get_path()
    def get_path(self, dumb):
        return self._get_path()

    def create(self, value): return super(ZKValueAccessor, self).create('', value)

    def delete(self, version=None): return super(ZKValueAccessor, self).delete('', version=None)

    def set(self, value, version=None): return super(ZKValueAccessor, self).set('', value, version=None)

    def get(self): return super(ZKValueAccessor, self).get('')


def rangeset_load(value):
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
    return {'txid': -1, 'value': None}, -1


class ZKStorage(TXStorageHelper):

    def __init__(self, zkclient):

        assert isinstance(zkclient, zkutil.KazooClientExt)

        self.zkclient = zkclient

        self.txidset = ZKValueAccessor(self.zkclient,
                                       self.zkclient._zkconf.txidset,
                                       load=rangeset_load)

        self.journal = ZKKVAccessor(self.zkclient,
                                    self.zkclient._zkconf.journal)

        self.record = ZKKVAccessor(self.zkclient,
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
