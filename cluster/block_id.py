#!/usr/bin/env python2
# coding: utf-8

from collections import namedtuple

from .block_group_id import BlockGroupID
from .block_index import BlockIndex
from .idbase import IDBase
from .server import DriveID

BlockIDLen = 48


class BlockBaseError(Exception):
    pass


class BlockIDError(BlockBaseError):
    pass


class BlockID(namedtuple('_BlockID', 'type block_group_id block_index drive_id block_id_seq'), IDBase):

    _tostr_fmt = '{type}{block_group_id}{block_index}{drive_id}{block_id_seq:0>10}'

    @classmethod
    def parse(cls, block_id):

        bid = str(block_id)

        if len(bid) != BlockIDLen:
            raise BlockIDError('Block id length should be {0}, but is {1}: {2}'.format(
                BlockIDLen, len(bid), bid))

        return BlockID(bid[:2],
                       bid[2:18],
                       bid[18:22],
                       bid[22:38],
                       bid[-10:])

    def __new__(clz, type, block_group_id, block_index, drive_id, block_id_seq):

        if not isinstance(block_group_id, BlockGroupID):
            block_group_id = BlockGroupID.parse(block_group_id)

        if not isinstance(block_index, BlockIndex):
            block_index = BlockIndex.parse(block_index)

        if not isinstance(drive_id, DriveID):
            drive_id = DriveID.parse(drive_id)

        block_id_seq = int(block_id_seq)

        return super(BlockID, clz).__new__(clz, type, block_group_id, block_index, drive_id, block_id_seq)
