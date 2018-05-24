#!/usr/bin/env python
# coding: utf-8


class KeyValue(object):

    def create(self, key, value): raise TypeError('unimplemented')

    def delete(self, key, version=None): raise TypeError('unimplemented')

    def set(self, key, value, version=None): raise TypeError('unimplemented')

    def get(self, key): raise TypeError('unimplemented')


class Value(object):

    def create(self, value): raise TypeError('unimplemented')

    def delete(self, version=None): raise TypeError('unimplemented')

    def set(self, value, version=None): raise TypeError('unimplemented')

    def get(self): raise TypeError('unimplemented')
