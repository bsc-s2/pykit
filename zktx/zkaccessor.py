#!/usr/bin/env python
# coding: utf-8

import logging

from kazoo.exceptions import NodeExistsError
from kazoo.exceptions import NoNodeError

logger = logging.getLogger(__name__)


class ZKKeyValue(object):
    def __init__(self, zkclient, get_path=None, load=None, dump=None, nonode_callback=None):

        self.zkclient = zkclient
        self._get_path = get_path
        self.load = load
        self.dump = dump
        self.nonode_callback = nonode_callback

    def get_path(self, key):
        if self._get_path is None:
            return key
        else:
            return self._get_path(key)

    def create(self, key, value, ephemeral=False, sequence=False):

        value = self._dump(value)
        return self.zkclient.create(self.get_path(key), value, acl=self._get_acl(),
                                    ephemeral=ephemeral, sequence=sequence)

    def delete(self, key, version=-1):
        return self.zkclient.delete(self.get_path(key), version=version)

    def set(self, key, value, version=-1):
        value = self._dump(value)
        self.zkclient.set(self.get_path(key), value, version=version)

    def set_or_create(self, key, value, version=-1):

        value = self._dump(value)
        while True:
            try:
                self.zkclient.set(self.get_path(key), value, version=version)
                return
            except NoNodeError:
                if version == -1:
                    try:
                        self.zkclient.create(self.get_path(key), value, acl=self._get_acl())
                        return
                    except NodeExistsError:
                        continue
                else:
                    raise

    def get(self, key):
        try:
            val, zstat = self.zkclient.get(self.get_path(key))
            version = zstat.version
        except NoNodeError:
            if self.nonode_callback is not None:
                val, version = self.nonode_callback()
            else:
                raise
        return self._load(val), version

    def _load(self, val):
        if self.load is not None:
            return self.load(val)
        else:
            return val

    def _dump(self, val):
        if self.dump is not None:
            return self.dump(val)
        else:
            return val

    def _get_acl(self):
        acl = None
        zkconf = getattr(self.zkclient, '_zkconf', None)
        if zkconf is not None:
            acl = zkconf.kazoo_digest_acl()
        return acl


class ZKValue(ZKKeyValue):
    def get_path(self, key):
        return self._get_path()

    def create(self, value, ephemeral=False, sequence=False):
        return super(ZKValue, self).create('', value,
                                           ephemeral=ephemeral, sequence=sequence)

    def delete(self, version=-1):
        return super(ZKValue, self).delete('', version=version)

    def set(self, value, version=-1):
        return super(ZKValue, self).set('', value, version=version)

    def set_or_create(self, value, version=-1):
        return super(ZKValue, self).set_or_create('', value, version=version)

    def get(self):
        return super(ZKValue, self).get('')
