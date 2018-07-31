#!/usr/bin/env python
# coding: utf-8

import logging

from pykit import config
from pykit import utfjson

from .redisaccessor import RedisKeyValue
from .redisaccessor import RedisValue
from .status import STATUS
from .storage import Storage
from . import zkstorage

logger = logging.getLogger(__name__)


class RedisStorage(Storage):

    def __init__(self, redis_cli, journal_id_set_path):
        self.redis_cli = redis_cli
        self.journal_id_set_path = journal_id_set_path

        self.journal_id_set = RedisValue(self.redis_cli,
                                         get_path=self._journal_id_set_path,
                                         load=_journal_id_set_load)

        self.record = RedisKeyValue(self.redis_cli)

    def _journal_id_set_path(self):
        return self.journal_id_set_path or getattr(config, 'redis_journal_id_set_path')

    def apply_jour(self, jour):
        for k, v in jour.items():
            self.apply_record(k, v)

    def apply_record(self, key, val):
        # meta/server/<server_id>
        # meta/region/<region_id>
        k_parts = key.split('/', 2)
        if len(k_parts) != 3:
            raise KeyError('invalid key: {k}'.format(k=key))

        if k_parts[0] != 'meta':
            logger.info('{k} no need to save'.format(k=key))
            return

        hashname = k_parts[1]
        hashkey = k_parts[2]
        if val is None:
            self.record.hdel(hashname, hashkey)
            return

        self.record.hset(hashname, hashkey, val)

    def delete_absent_record(self, existed):
        for hname in existed:
            to_purged = []
            hkeys = self.record.hkeys(hname)
            for k in hkeys:
                if k not in existed[hname]:
                    to_purged.append(k)

            if len(to_purged) > 0:
                self.record.hdel(hname, *to_purged)

    def add_to_journal_id_set(self, status, journal_id):
        if status not in STATUS:
            raise KeyError('invalid status: ' + repr(status))

        journal_id_set = self.journal_id_set.get()
        journal_id_set[status].add([journal_id, journal_id + 1])

        self.journal_id_set.set(journal_id_set)

    def set_journal_id_set(self, journal_id_set):
        self.journal_id_set.set(journal_id_set)


def _journal_id_set_load(value):
    return zkstorage.journal_id_set_load(utfjson.load(value) or {})
