#!/usr/bin/env python2
# coding: utf-8

from collections import namedtuple

from .block_group_id import BlockGroupID
from .idbase import IDBase
from .server import DriveID

BlockIDLen = 48


class BlockBaseError(Exception):
    pass


class BlockIDError(BlockBaseError):
    pass


class BlockID(namedtuple('_BlockID', 'type block_group_id block_index drive_id pg_seq'), IDBase):

    _tostr_fmt = '{type}{block_group_id}{block_index}{drive_id}{pg_seq:0>10}'

    @classmethod
    def parse(cls, block_id):

        if len(block_id) != BlockIDLen:
            raise BlockIDError('Block id length should be {0}, but is {1}: {2}'.format(
                BlockIDLen, len(block_id), block_id))

        return BlockID(block_id[:2],
                       block_id[2:18],
                       block_id[18:22],
                       block_id[22:38],
                       block_id[-10:])

    def __new__(clz, type, block_group_id, block_index, drive_id, pg_seq):

        if isinstance(block_group_id, BlockGroupID):
            pass
        else:
            block_group_id = BlockGroupID.parse(block_group_id)

        if isinstance(drive_id, DriveID):
            pass
        else:
            drive_id = DriveID.parse(drive_id)

        pg_seq = int(pg_seq)

        return super(BlockID, clz).__new__(clz, type, block_group_id, block_index, drive_id, pg_seq)
