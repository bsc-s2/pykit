#!/usr/bin/env python
# coding: utf-8

import threading
import logging

from kazoo.exceptions import NoNodeError

from pykit import rangeset
from pykit import zkutil
from pykit import jobq
from pykit import cachepool

from .status import COMMITTED
from .status import PURGED
from .zkaccessor import ZKKeyValue
from .zkaccessor import ZKValue
from .zkstorage import record_nonode_cb
from .zkstorage import journal_id_set_load

logger = logging.getLogger(__name__)


class SlaveError(Exception):
    pass


class Slave(object):

    def __init__(self, zke, storage):
        assert isinstance(zke, zkutil.KazooClientExt)

        self.zke = zke
        self.storage = storage
        self.zk_journal_id_set = None

        self.journal_id_set = ZKValue(self.zke,
                                      self.zke._zkconf.journal_id_set,
                                      load=journal_id_set_load)

        self.journal = ZKKeyValue(self.zke,
                                  self.zke._zkconf.journal)

        self.record = ZKKeyValue(self.zke,
                                 self.zke._zkconf.record,
                                 nonode_callback=record_nonode_cb)

    def _get_uncommitted_journal_ids(self):
        storage_journal_id_set = self.storage.journal_id_set.get()

        subset = rangeset.substract(self.zk_journal_id_set[COMMITTED],
                                    storage_journal_id_set[COMMITTED])

        for begin, end in subset:
            for jid in range(begin, end):
                yield jid

    def _set_all_records(self):
        record_dir = self.zke._zkconf.record_dir()
        meta_path = ''.join([record_dir, 'meta'])
        names = self.zke.get_children(meta_path)

        lock = threading.RLock()
        st = {'existed': {}, 'failed': []}
        zke_pool = cachepool.CachePool(lambda c: zkutil.kazoo_client_ext(c)[0],
                                       generator_args=[self.zke._zkconf],
                                       close_callback=zkutil.close_zk)

        def _iter_key():
            for n in names:
                keys_path = '/'.join([meta_path, n])
                keys = self.zke.get_children(keys_path)

                with lock:
                    if n not in st['existed']:
                        st['existed'][n] = {}

                for k in keys:
                    path = '/'.join([keys_path, k])
                    yield (n, k, path)

        def _set_record(args):
            try:
                n, k, path = args
                try:
                    with cachepool.make_wrapper(zke_pool)() as zke:
                        val, _ = zke.get(path)
                except NoNodeError:
                    # the node may be deleted after get children
                    logger.warn('{p} has been deleted'.format(p=path))
                    return

                # k='record_dir/meta/server/<server_id>
                # remove record_dir
                path = path[len(record_dir):]
                self.storage.apply_record(path, val[-1])

                with lock:
                    st['existed'][n][k] = 1

            except Exception as e:
                logger.exception(repr(e) + ' while set record {a}'.format(a=args))
                with lock:
                    st['failed'].append(args)

        jobq.run(_iter_key(), [(_set_record, 20)])
        if len(st['failed']) > 0:
            logger.error('failed to set record {f}'.format(f=st['failed']))
            raise SlaveError('failed to set record')

        while not zke_pool.queue.empty():
            ele = zke_pool.queue.get()
            zkutil.close_zk(ele)

        self.storage.delete_absent_record(st['existed'])
        self.storage.set_journal_id_set(self.zk_journal_id_set)

    def apply(self):
        self.zk_journal_id_set, _ = self.journal_id_set.get()

        for journal_id in self._get_uncommitted_journal_ids():

            try:
                if self.zk_journal_id_set[PURGED].has(journal_id):
                    raise NoNodeError('journal {jid:0>10} has been deleted'.format(jid=journal_id))

                jour, _ = self.journal.get(journal_id)

            except NoNodeError:
                logger.warn('journal not found journal id: {jid:0>10}'.format(jid=journal_id))
                self._set_all_records()
                return

            self.storage.apply_jour(jour)
            self.storage.add_to_journal_id_set(COMMITTED, journal_id)
