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

        size = int(block_group_id[1:6])
        seq = int(block_group_id[6:])

        return BlockGroupID(size, seq)

    def __str__(self):

        blk_size = '%05d' % self.block_size
        seq = '%010d' % self.seq

        return 'g' + blk_size + seq
