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

    def purge(self, sets):

        committed_set = sets[COMMITTED]
        length = committed_set.length()

        if length <= self.max_journal_history:
            return

        purged_set = sets[PURGED]
        purged_end_jid = length - self.max_journal_history

        topurge = rangeset.RangeSet()
        for jid in range(purged_end_jid):
            if purged_set.has(jid):
                continue

            topurge.add([jid, jid + 1])

        for rng in topurge:
            for jid in range(rng[0], rng[1]):
                self.journal.safe_delete(jid)

        sets[PURGED] = rangeset.union(sets[PURGED], topurge)

    def add_to_journal_id_set(self, status, journal_id):

        if status not in STATUS:
            raise KeyError('invalid status: ' + repr(status))

        logger.info('add {st} journal id: {jid}'.format(st=status, jid=journal_id))

        for curr in txutil.cas_loop(self.journal_id_set.get,
                                    self.journal_id_set.set,
                                    conflicterror=self.conflicterror):

            for st in STATUS:
                if st not in curr.v:
                    curr.v[st] = rangeset.RangeSet([])

            if status == COMMITTED:
                curr.v[status].add([0, int(journal_id) + 1])
            else:
                curr.v[status].add([journal_id, int(journal_id) + 1])

            self.purge(curr.v)


class Storage(StorageHelper):

    record = KeyValue()
    journal = KeyValue()
    journal_id_set = Value()

    def acquire_key_loop(self, txid, key): raise TypeError('unimplemented')

    def try_release_key(self, txid, key): raise TypeError('unimplemented')
