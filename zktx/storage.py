#!/usr/bin/env python
# coding: utf-8

import logging

from pykit import rangeset
from pykit import txutil

from .accessor import KeyValue
from .accessor import Value
from .status import COMMITTED
from .status import PURGED
from .status import STATUS

logger = logging.getLogger(__name__)


class StorageHelper(object):

    max_value_history = 16     # keeps the last n modifications in a record
    max_journal_history = 1024  # keeps the last n committed journal
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

            self.purge(curr.v)

    def purge(self, sets):

        topurge = rangeset.RangeSet()

        committed = sets[COMMITTED]
        l = committed.length()

        while l > self.max_journal_history:

            first = committed[0]

            # a range contains a single txid
            r = rangeset.RangeSet([[first[0], first[0] + 1]])

            topurge.add(r[0])
            committed = rangeset.substract(committed, r)
            l -= 1

        for rng in topurge:

            for txid in range(rng[0], rng[1]):
                self.journal.safe_delete(txid)

        sets[PURGED] = rangeset.union(sets[PURGED], topurge)
        sets[COMMITTED] = rangeset.substract(sets[COMMITTED], topurge)


class Storage(StorageHelper):

    record = KeyValue()
    journal = KeyValue()
    txidset = Value()

    def acquire_key_loop(self, txid, key): raise TypeError('unimplemented')

    def try_release_key(self, txid, key): raise TypeError('unimplemented')
