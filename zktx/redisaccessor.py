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
        hashkey = self._get_path(hashkey)
        val = self.cli.hget(hashname, hashkey)

        if self.load is not None:
            return self.load(val)

        return utfjson.load(val)

    def hset(self, hashname, hashkey, value):
        hashkey = self._get_path(hashkey)
        value = utfjson.dump(value)
        self.cli.hset(hashname, hashkey, value)


class RedisValue(RedisKeyValue):

    def _get_path(self, key):
        return self.get_path()

    def set(self, value):
        return super(RedisValue, self).set('', value)

    def get(self):
        return super(RedisValue, self).get('')
