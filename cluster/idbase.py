#!/usr/bin/env python
# coding: utf-8

from pykit import utfjson


class IDBase(object):

    _tostr_fmt = '{item_1}-{item_2:0>3}'

    def __str__(self):
        return self._tostr_fmt.format(**{k: str(v) for k, v in self._asdict().items()})

    def tostr(self):
        return str(self)


def json_dump(obj, encoding='utf-8'):

    obj = encode_idbase(obj)

    return utfjson.dump(obj, encoding)


def json_load(s, encoding=None):
    return utfjson.load(s, encoding)


def encode_idbase(o):

    if isinstance(o, IDBase):
        return str(o)

    if isinstance(o, dict):
        rst = {}
        for k, v in o.items():
            rst[encode_idbase(k)] = encode_idbase(v)

    elif isinstance(o, (list, tuple)):
        rst = []
        for v in o:
            rst.append(encode_idbase(v))

    else:
        rst = o

    return rst
