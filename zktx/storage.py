#!/usr/bin/env python
# coding: utf-8

import logging

from pykit import rangeset
from pykit import txutil

from .accessor import KeyValue
from .accessor import Value
from .status import STATUS

logger = logging.getLogger(__name__)


class StorageHelper(object):

    # keeps the last n modifications in a record
    max_value_history = 16
    conflicterror = None

    def apply_record(self, txid, key, value):

        # the data in underlying storage is multi-version record:
        # [
        #     [<txid>, <value>]
        #     [<txid>, <value>]
        #     ...
        # ]

        for curr in txutil.cas_loop(self.record.get,
                                    self.record.set_or_create,
                                    args=(key, ),
                                    conflicterror=self.conflicterror):

            max_txid = curr.v[-1][0]

            if max_txid >= txid:
                return False

            curr.v.append((txid, value))
            while len(curr.v) > self.max_value_history:
                curr.v.pop(0)

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

    record = KeyValue()
    journal = KeyValue()
    txidset = Value()

    def acquire_key_loop(self, txid, key): raise TypeError('unimplemented')

    def try_release_key(self, txid, key): raise TypeError('unimplemented')
