#!/usr/bin/env python
# coding: utf-8


from .idbase import IDBase


def _idx(n):

    try:
        n = int(n)
    except ValueError:
        raise ValueError('index i and j must be int or int-str but: {n}'.format(n=n))

    if not (0 <= n <= 99):
        raise ValueError('index i and j must be 0~99, but: {n}'.format(n=n))

    return n


class BlockIndex(IDBase):

    _attrs = (
        ('i', 0, 2, _idx),
        ('j', 2, 4, _idx),
    )

    _str_len = 4

    _tostr_fmt = '{i:0>2}{j:0>2}'
