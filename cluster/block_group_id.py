#!/usr/bin/env python
# coding: utf-8

from collections import namedtuple

from .idbase import IDBase

BlockGroupIDLen = 16


class BlockGroupIDError(Exception):
    pass


class BlockGroupID(namedtuple('_BlockGroupID', 'block_size seq'), IDBase):

    _tostr_fmt = 'g{block_size:0>5}{seq:0>10}'

    @classmethod
    def parse(cls, block_group_id):
        if len(block_group_id) != BlockGroupIDLen:
            raise BlockGroupIDError('Block group id length should be {0}, but is {1}: {2}'.format(
                BlockGroupIDLen, len(block_group_id), block_group_id))

        size = int(block_group_id[1:6])
        seq = int(block_group_id[6:])

        return BlockGroupID(size, seq)

    def __new__(clz, block_size, seq):
        block_size = int(block_size)
        seq = int(seq)

        return super(BlockGroupID, clz).__new__(clz, block_size, seq)
