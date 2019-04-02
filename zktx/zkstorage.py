#!/usr/bin/env python
# coding: utf-8

import logging

from kazoo.exceptions import BadVersionError

from pykit import rangeset
from pykit import zkutil

from .status import STATUS
from .storage import Storage
from .zkaccessor import ZKKeyValue
from .zkaccessor import ZKValue

from .exceptions import NotLocked
from kazoo.exceptions import NoNodeError

logger = logging.getLogger(__name__)


class ZKStorage(Storage):

    conflicterror = BadVersionError

    def __init__(self, zke):

        assert isinstance(zke, zkutil.KazooClientExt)

        self.zke = zke

        self.journal_id_set = ZKValue(self.zke,
                                      self.zke._zkconf.journal_id_set,
                                      load=journal_id_set_load)

        self.journal = ZKKeyValue(self.zke,
                                  self.zke._zkconf.journal)

        self.record = ZKKeyValue(self.zke,
                                 self.zke._zkconf.record,
                                 nonode_callback=record_nonode_cb)

        self.state = ZKKeyValue(self.zke,
                                self.zke._zkconf.tx_state,
                                nonode_callback=state_nonode_cb)

    def acquire_key_loop(self, txid, key, timeout):
        logger.info('watch acquire: {txid} {key}'.format(txid=txid, key=key))

        keylock = self._make_key_lock(txid, key)

        for holder, ver in keylock.acquire_loop(timeout=timeout):
            # int(txid)
            holder['id'] = int(holder['id'])
            yield holder, ver

        # locked
        holder, ver = keylock.lock_holder
        holder['id'] = int(holder['id'])

        yield holder, ver

    def set_lock_key_val(self, txid, key, val, version=-1):
        logger.info('set: {txid} {key} {val} {ver}'.format(
            txid=txid, key=key, val=val, ver=version))

        keylock = self._make_key_lock(txid, key)

        try:
            return keylock.set_lock_val(val, version)
        except NoNodeError:
            raise NotLocked("Not allowed to set non-locked: {k}".format(k=key))

    def try_release_key(self, txid, key):

        logger.info('releasing: {txid} {key}'.format(txid=txid, key=key))

        keylock = self._make_key_lock(txid, key)

        locked, holder, ver = keylock.try_acquire()
        if locked:
            keylock.release()
        else:
            keylock.close()

        return locked, int(holder['id']), ver

    def _make_key_lock(self, txid, key):
        ident = zkutil.make_identifier(txid, None)
        keylock = zkutil.ZKLock(key,
                                zkclient=self.zke,
                                zkconf=self.zke._zkconf,
                                ephemeral=False,
                                identifier=ident)

        return keylock


def journal_id_set_load(value):
    rst = {}
    for k in STATUS:
        if k not in value:
            value[k] = []
        rst[k] = rangeset.RangeSet(value[k])
    return rst


def record_nonode_cb():
    """
    If NoNodeError received, make a default value for a record
    """

    return [None], -1


def state_nonode_cb():
    return None, -1
