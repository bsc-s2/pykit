#!/usr/bin/env python
# coding: utf-8

from collections import namedtuple

from .idbase import IDBase


class BlockIndexError(ValueError):
    pass


class BlockIndex(namedtuple('_BlockIndex', 'i j'), IDBase):

    _tostr_fmt = '{i:0>2}{j:0>2}'

    @classmethod
    def parse(clz, block_index):
        if len(block_index) != 4:
            raise BlockIndexError('block_index len must be 4, but: {bi}'.format(
                bi=block_index))

        ii, jj = block_index[:2], block_index[2:]

        return BlockIndex(ii, jj)

    def __new__(clz, i, j):
        try:
            i = int(i)
            j = int(j)
        except ValueError:
            raise BlockIndexError('index i and j must be int or int-str but: {i} {j}'.format(i=i, j=j))

        if not (0 <= i <= 99):
            raise BlockIndexError('idc index must be 0~99, but: {i}'.format(i=i))
        if not (0 <= j <= 99):
            raise BlockIndexError('cross idc index must be 0~99, but: {j}'.format(j=j))

        return super(BlockIndex, clz).__new__(clz, i, j)
