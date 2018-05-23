#!/usr/bin/env python
# coding: utf-8

import logging

from pykit import rangeset
from pykit import txutil

from .accessor import KVAccessor
from .accessor import ValueAccessor
from .status import STATUS

logger = logging.getLogger(__name__)


class StorageHelper(object):

    # keeps the last n modifications in a record
    max_value_history = 16
    conflicterror = None

    def get_latest(self, key):
        """
        return: (
                    {<txid> : <value>},
                    zk_version,
                )
        """

        c, ver = self.record.get(key)

        txids = sorted(c.keys())
        max_txid = txids[-1]
        return (max_txid, c[max_txid]), ver

    def apply_record(self, txid, key, value):

        # the data in underlying storage is multi-version record:
        # {
        #     <txid>: <value>
        #     <txid>: <value>
        #     ...
        # }

        for curr in txutil.cas_loop(self.record.get,
                                    self.record.set_or_create,
                                    args=(key, ),
                                    conflicterror=self.conflicterror):

            max_txid = -1
            txids = sorted(curr.v.keys())
            if len(txids) > 0:
                max_txid = max(txids)

            if max_txid >= txid:
                return False

            curr.v[txid] = value
            if len(curr.v) > self.max_value_history:
                del curr.v[txids[0]]

        return True

    def add_to_txidset(self, status, txid):

        if status not in STATUS:
            raise KeyError('invalid status: ' + repr(status))

        logger.info('add {status}:{txid}'
                    ' to txidset'.format(
                        status=status, txid=txid))

        for curr in txutil.cas_loop(self.txidset.get,
                                    self.txidset.set,
                                    conflicterror=self.conflicterror):

            for st in STATUS:
                if st not in curr.v:
                    curr.v[st] = rangeset.RangeSet([])

            curr.v[status].add([txid, txid + 1])


class Storage(StorageHelper):

    record = KVAccessor()
    journal = KVAccessor()
    txidset = ValueAccessor()

    def watch_acquire_key(self, txid, key): raise TypeError('unimplemented')

    def try_release_key(self, txid, key): raise TypeError('unimplemented')
