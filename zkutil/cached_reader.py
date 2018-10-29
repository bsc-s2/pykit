#!/usr/bin/env python2
# coding: utf-8

import logging
import threading

from . import zkconf
from . import zkutil
from . import exceptions

logger = logging.getLogger(__name__)


class CachedReader(dict):

    def __init__(self, zk, path, callback=None):
        super(CachedReader, self).__init__()

        self.zke, self.owning_zk = zkconf.kazoo_client_ext(zk)
        self.path = path
        self.callback = callback
        self.available_ev = threading.Event()
        self.stopped = False
        self.val = [None, None]
        # lock for update the dict
        self.lock = threading.RLock()

        def _conn_change_cb(state):
            self._on_conn_change(state)

        def _node_change_cb(event):
            self._on_node_change(event)

        self.conn_change_cb = _conn_change_cb
        self.node_change_cb = _node_change_cb
        self.zke.add_listener(self.conn_change_cb)
        self._update()

    def watch(self, timeout=None):
        self.available_ev.clear()

        timeout = timeout or 86400 * 365

        if self.available_ev.wait(timeout):
            if self.stopped:
                return None

            else:
                return self.val

        else:
            raise exceptions.ZKWaitTimeout('timeout {t} sec'.format(t=timeout))

    def close(self):
        self.stopped = True
        self.available_ev.set()

        self.zke.remove_listener(self.conn_change_cb)
        if self.owning_zk:
            zkutil.close_zk(self.zke)

    def _on_conn_change(self, state):
        logger.info('state changed: {state}'.format(state=state))
        self.stopped = True
        self.available_ev.set()

    def _on_node_change(self, event):
        logger.info('node state changed:{ev}'.format(ev=event))

        if self.stopped:
            return

        self._update()
        self.available_ev.set()

        if self.callback is None:
            return

        self.callback(self.path, self.val[0], self.val[1])

    def _update(self):
        with self.lock:
            curr, _ = self.zke.get(self.path, watch=self.node_change_cb)
            self.val = [self.val[1], curr]
            self.update(curr)

            keys = self.keys()
            for k in keys:
                if k not in curr:
                    del self[k]
