#!/usr/bin/env python2
# coding: utf-8

from collections import namedtuple

from .server import DriveID

BlockIDLen = 48


class BlockBaseError(Exception):
    pass


class BlockIDError(BlockBaseError):
    pass


class BlockID(namedtuple('_BlockID', 'type block_group_id block_index drive_id pg_seq')):

    @classmethod
    def parse(cls, block_id):

        if len(block_id) != BlockIDLen:
            raise BlockIDError('Block id length should be {0}, but is {1}: {2}'.format(
                BlockIDLen, len(block_id), block_id))

        pg_seq = int(block_id[-10:])

        return BlockID(block_id[:2], block_id[2:18], block_id[18:22], DriveID.parse(block_id[22:38]), pg_seq)

    def __init__(self, type, block_group_id, block_index, drive_id, pg_seq):
        if isinstance(drive_id, DriveID):
            pass
        else:
            drive_id = DriveID.parse(drive_id)

        super(BlockID, self).__init__(type, block_group_id, block_index, drive_id, pg_seq)

    def __str__(self):

        pg_seq = '%010d' % self.pg_seq

        return self.type + self.block_group_id + self.block_index + self.drive_id.tostr() + pg_seq

    def tostr(self):
        return str(self)
