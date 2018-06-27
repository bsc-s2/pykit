#!/usr/bin/env python
# coding: utf-8

import logging

from pykit import config
from pykit import rangeset
from pykit import utfjson

from .redisaccessor import RedisKeyValue
from .redisaccessor import RedisValue
from .status import COMMITTED
from .status import STATUS
from .storage import Storage

logger = logging.getLogger(__name__)


class RedisStorage(Storage):

    def __init__(self, redis_cli, txidset_path):
        self.redis_cli = redis_cli
        self.txidset_path = txidset_path

        self.txidset = RedisValue(self.redis_cli,
                                  get_path=self._txidset_path,
                                  load=txidset_load)
        self.record = RedisKeyValue(self.redis_cli)

    def _txidset_path(self):
        return self.txidset_path or getattr(config, 'redis_txidset_path')

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

        self.record.hset(hashname, hashkey, val)

    def add_to_txidset(self, status, txid):
        if status not in STATUS:
            raise KeyError('invalid status: ' + repr(status))

        txidset = self.txidset.get()
        txidset[status].add([txid, txid + 1])

        self.txidset.set(txidset)

    def set_txidset(self, status, txidset):
        val = {
            status: txidset,
        }
        self.txidset.set(val)


def txidset_load(value):
    val = utfjson.load(value)
    if val is None:
        val = {}

    committed = val.get(COMMITTED) or []

    rst = {}
    rst[COMMITTED] = rangeset.RangeSet(committed)

    return rst
