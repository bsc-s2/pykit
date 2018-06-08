#!/usr/bin/env python
# coding: utf-8

import logging

from kazoo.exceptions import NoNodeError

from pykit import rangeset
from pykit import zkutil

from .status import COMMITTED
from .zkaccessor import ZKKeyValue
from .zkaccessor import ZKValue
from .zkstorage import record_nonode_cb
from .zkstorage import txidset_load

logger = logging.getLogger(__name__)


class Slave(object):

    def __init__(self, zke, storage):
        assert isinstance(zke, zkutil.KazooClientExt)

        self.zke = zke
        self.storage = storage
        self.zk_cmt_txidset = None

        self.txidset = ZKValue(self.zke,
                               self.zke._zkconf.txidset,
                               load=txidset_load)

        self.journal = ZKKeyValue(self.zke,
                                  self.zke._zkconf.journal)

        self.record = ZKKeyValue(self.zke,
                                 self.zke._zkconf.record,
                                 nonode_callback=record_nonode_cb)

    def _get_uncommitted_txids(self):
        storage_txidset = self.storage.txidset.get()

        subset = rangeset.substract(self.zk_cmt_txidset, storage_txidset[COMMITTED])

        for begin, end in subset:
            for i in range(begin, end):
                yield i

    def _get_all_records(self):
        record_dir = self.zke._zkconf.record_dir()
        meta_path = ''.join([record_dir, 'meta'])
        names = self.zke.get_children(meta_path)

        rst = {}
        for n in names:
            keys_path = '/'.join([meta_path, n])
            keys = self.zke.get_children(keys_path)

            for k in keys:
                path = '/'.join([keys_path, k])
                val, _ = self.zke.get(path)

                # k='record_dir/meta/server/<server_id>
                # remove record_dir
                path = path[len(record_dir):]
                rst[path] = val

        return rst

    def _set_all_records(self):
        records = self._get_all_records()
        for k, v in records.items():

            while len(v) > 0:
                txid = v[-1][0]
                if not self.zk_cmt_txidset.has(txid):
                    v.pop()
                    logger.warn('txid {txid} not in {cmt_txids}'.format(
                        txid=txid, cmt_txids=self.zk_cmt_txidset))

                else:
                    break

            else:
                logger.error('record {k} txids {txids} not in {cmt_txids}'.format(
                    k=k, txids=v, cmt_txids=self.zk_cmt_txidset))
                continue

            self.storage.apply_record(k, v[-1][1])

        self.storage.set_txidset(COMMITTED, self.zk_cmt_txidset)

    def apply(self):
        sets, _ = self.txidset.get()
        self.zk_cmt_txidset = sets[COMMITTED]

        for txid in self._get_uncommitted_txids():

            try:
                jour, _ = self.journal.get(txid)

            except NoNodeError:
                logger.warn('jour not found txid: {txid}'.format(txid=txid))
                self._set_all_records()
                return

            self.storage.apply_jour(jour)
            self.storage.add_to_txidset(COMMITTED, txid)
