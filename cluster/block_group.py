#!/usr/bin/env python2
# coding: utf-8

from collections import namedtuple


class BlockGroupBaseError(Exception):
    pass


class BlockGroupIDError(Exception):
    pass


class BlockGroupID(namedtuple('_BlockGroupID', 'block_size seq')):

    @classmethod
    def parse(cls, block_group_id):

        if len(block_group_id) != 16:
            raise BlockGroupIDError(block_group_id)

        return BlockGroupID(block_group_id[1:6], block_group_id[6:])

    def __str__(self):
        return 'g' + self.block_size + self.seq
