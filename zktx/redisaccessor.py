#!/usr/bin/env python
# coding: utf-8

from pykit import utfjson


class RedisKeyValue(object):

    def __init__(self, redis_cli, get_path=None, load=None):
        self.cli = redis_cli
        self.get_path = get_path
        self.load = load

    def _get_path(self, key):
        if self.get_path is not None:
            return self.get_path(key)

        return key

    def set(self, key, value):
        key = self._get_path(key)
        value = utfjson.dump(value)
        self.cli.set(key, value)

    def get(self, key):
        key = self._get_path(key)
        val = self.cli.get(key)

        if self.load is not None:
            return self.load(val)

        return utfjson.load(val)

    def hget(self, hashname, hashkey):
        hashname = self._get_path(hashname)
        val = self.cli.hget(hashname, hashkey)

        if self.load is not None:
            return self.load(val)

        return utfjson.load(val)

    def hset(self, hashname, hashkey, value):
        hashname = self._get_path(hashname)
        value = utfjson.dump(value)
        self.cli.hset(hashname, hashkey, value)

    def hdel(self, hashname, *keys):
        hashname = self._get_path(hashname)
        self.cli.hdel(hashname, *keys)

    def hkeys(self, hashname):
        hashname = self._get_path(hashname)
        return self.cli.hkeys(hashname)


class RedisValue(RedisKeyValue):

    def _get_path(self, key):
        return self.get_path()

    def set(self, value):
        return super(RedisValue, self).set('', value)

    def get(self):
        return super(RedisValue, self).get('')
