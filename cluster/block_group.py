#!/usr/bin/env python2
# coding: utf-8

from collections import namedtuple

BlockGroupIDLen = 16


class BlockGroupBaseError(Exception):
    pass


class BlockGroupIDError(Exception):
    pass


class BlockGroupID(namedtuple('_BlockGroupID', 'block_size seq')):

    @classmethod
    def parse(cls, block_group_id):

        if len(block_group_id) != BlockGroupIDLen:
            raise BlockGroupIDError('Block group id length should be {0}, but is {1}: {2}'.format(
                BlockGroupIDLen, len(block_group_id), block_group_id))

        return BlockGroupID(block_group_id[1:6], block_group_id[6:])

    def __str__(self):
        return 'g' + self.block_size + self.seq
