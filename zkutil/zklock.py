#!/usr/bin/env python
# coding: utf-8

import logging
import threading
import time

from kazoo.client import KazooClient
from kazoo.exceptions import KazooException
from kazoo.exceptions import LockTimeout
from kazoo.exceptions import NodeExistsError
from kazoo.exceptions import NoNodeError

from . import zkutil
from .zkconf import ZKConf

logger = logging.getLogger(__name__)


class ZKTXError(Exception):
    pass


class ZKTXConnectionLost(ZKTXError):
    pass


# TODO add method: ZKLock.get_owner() to get current lock owner
class ZKLock(object):

    def __init__(self, lock_name,
                 zkconf=None,
                 zkclient=None,
                 on_lost=None,
                 identifier=None,
                 ephemeral=True,
                 timeout=10):

        if zkconf is None:
            zkconf = ZKConf()
        if isinstance(zkconf, dict):
            zkconf = ZKConf(**zkconf)
        self.zkconf = zkconf

        if zkclient is None:
            # If user does not pass a zkclient instance,
            # we need to create one for lock to use.
            # This zkclient will be closed after lock is released

            if on_lost is None:
                raise ValueError('on_lost must be specified to watch zk connection issue if no zkclient specified')

            zkclient = make_owning_zkclient(zkconf.hosts(), zkconf.auth())
            self.owning_client = True
        else:
            self.owning_client = False

        if identifier is None:
            identifier = zkutil.lock_id(zkconf.node_id())

        # a copy of hosts for debugging and tracking
        self._hosts = ','.join(['{0}:{1}'.format(*x)
                                for x in zkclient.hosts])

        self.zkclient = zkclient
        self.on_lost = on_lost

        self.lock_name = lock_name
        self.lock_path = zkconf.lock(self.lock_name)
        self.identifier = identifier
        self.ephemeral = ephemeral
        self.timeout = timeout

        self.mutex = threading.RLock()
        self.maybe_available = threading.Event()
        self.maybe_available.set()
        self.lock_holder = None

        logger.info('adding event listener: {s}'.format(s=self))
        self.zkclient.add_listener(self.on_connection_change)

    def on_node_change(self, watchevent):

        # Must be locked first.
        # Or there is a chance on_node_change is triggered before
        #         self.maybe_available.clear()
        with self.mutex:
            self.maybe_available.set()

            # If locked. the node change is treated as losing a lock
            if self.is_locked():
                if self.on_lost is not None:
                    self.on_lost()

        logger.info('node state changed:{ev}, lock might be released: {s}'.format(ev=watchevent, s=str(self)))

    def on_connection_change(self, state):

        # notify zklock to re-do acquiring procedure, to trigger Connection Error
        with self.mutex:
            self.maybe_available.set()

        if self.on_lost is not None:
            self.on_lost()

    def acquire_loop(self, timeout=None):

        if timeout is None:
            timeout = self.timeout

        expire_at = time.time() + timeout

        while True:

            # Even if timeout is smaller than 0, try-loop continue on until
            # maybe_available is not ready.
            #
            # There is a chance that:
            #  - Failed to create lock node(lock is occupied by other)
            #  - Failed to get lock node(just deleted)
            #  - Failed to create lock node(lock is occupied by other)
            #  - Failed to get lock node(just deleted)
            #  - ...
            if not self.maybe_available.wait(timeout=expire_at - time.time()):

                logger.debug('lock is still held by others: ' + str(self))

                if time.time() > expire_at:
                    raise LockTimeout('lock: ' + str(self.lock_path))

            # Always proceed the "get" phase, in order to add a watch handler.
            # To watch node change event.

            self._create()
            self._acquire_by_get()
            if self.is_locked():
                return

            # If it is possible to acquire the lock in next retry, do not yield
            if self.maybe_available.is_set():
                continue
            else:
                yield self.lock_holder[0], self.lock_holder[1]

    def acquire(self, timeout=None):

        for holder, ver in self.acquire_loop(timeout=timeout):
            continue

    def try_acquire(self):

        try:
            self.acquire(timeout=-1)
        except LockTimeout:
            pass

        # if_locked, lock holder identifier, holder version
        return self.is_locked(), self.lock_holder[0], self.lock_holder[1]

    def try_release(self):

        logger.debug('try to release if I am locker holder: {s}'.format(s=str(self)))

        try:
            holder, zstat = self.zkclient.get(self.lock_path)
            self.lock_holder = (holder, zstat.version)

            logger.debug('got lock holder: {s}'.format(s=str(self)))

            if holder == self.identifier:

                self.zkclient.remove_listener(self.on_connection_change)

                try:
                    self.zkclient.delete(self.lock_path, version=zstat.version)
                except NoNodeError as e:
                    logger.info(repr(e) + ' while delete lock: ' + str(self))

                self.lock_holder = None

                return True, holder, zstat.version
            else:
                return False, holder, zstat.version

        except NoNodeError as e:
            logger.info(repr(e) + ' while try_release: {s}'.format(s=str(self)))
            return True, self.identifier, -1

    def release(self):

        with self.mutex:

            if self.is_locked():

                # remove listener to avoid useless event triggering
                self.zkclient.remove_listener(self.on_connection_change)

                try:
                    self.zkclient.delete(self.lock_path)
                except NoNodeError as e:
                    logger.info(repr(e) + ' while delete lock: ' + str(self))

                self.lock_holder = None

                logger.info('RELEASED: {s}'.format(s=str(self)))
            else:
                logger.info('not acquired, do not need to release')

        self.close()

    def close(self):

        self.zkclient.remove_listener(self.on_connection_change)

        if self.owning_client:

            logger.info('zk client is made by me, close it')

            try:
                self.zkclient.stop()
            except KazooException as e:
                logger.info(repr(e) + ' while stop my own client')

    def is_locked(self):

        l = self.lock_holder

        return (l is not None
                and l[0] == self.identifier)

    def _create(self):

        logger.debug('to creaet: {s}'.format(s=str(self)))

        try:
            self.zkclient.create(self.lock_path,
                                 self.identifier,
                                 ephemeral=self.ephemeral,
                                 acl=self.zkconf.kazoo_digest_acl())

        except NodeExistsError as e:

            # NOTE Success create on server side might also results in failure
            # on client side due to network issue.
            # 'get' after 'create' to check if existent node belongs to this
            # client.

            logger.debug(repr(e) + ' while create lock: {s}'.format(s=str(self)))
            self.lock_holder = None
            return

        logger.info('CREATE OK: {s}'.format(s=str(self)))

    def _acquire_by_get(self):

        logger.debug('to get: {s}'.format(s=str(self)))

        try:
            with self.mutex:

                holder, zstat = self.zkclient.get(self.lock_path, watch=self.on_node_change)
                self.lock_holder = (holder, zstat.version)

                logger.debug('got lock holder: {s}'.format(s=str(self)))

                if holder == self.identifier:
                    logger.info('ACQUIRED: {s}'.format(s=str(self)))
                    return

                logger.debug('other holds: {s}'.format(s=str(self)))
                self.maybe_available.clear()

        except NoNodeError as e:
            # create failed but when getting  it, it has been deleted
            logger.info(repr(e) + ' while get lock: {s}'.format(s=str(self)))
            with self.mutex:
                self.lock_holder = None
                self.maybe_available.set()

    def __str__(self):
        return '<id={id} {l}:[{holder}] on {h}>'.format(
            id=self.identifier,
            l=self.lock_path,
            holder=(self.lock_holder or ''),
            h=str(self._hosts),
        )

    def __enter__(self):
        self.acquire()

    def __exit__(self, tp, value, tb):
        self.release()


def make_owning_zkclient(hosts, auth):

    zkclient = KazooClient(hosts=hosts)
    zkclient.start()

    if auth is not None:
        scheme, name, passw = auth
        zkclient.add_auth(scheme, name + ':' + passw)

    return zkclient
