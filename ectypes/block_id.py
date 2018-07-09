#!/usr/bin/env python2
# coding: utf-8


from .block_group_id import BlockGroupID
from .block_index import BlockIndex
from .idbase import IDBase
from .server import DriveID


class BlockID(IDBase):
    _attrs = (
        ('type',           0,  2,  str),
        ('block_group_id', 2,  18, BlockGroupID),
        ('block_index',    18, 22, BlockIndex),
        ('drive_id',       22, 38, DriveID),
        ('block_id_seq',   38, 48, int),
    )

    _str_len = 48

    _tostr_fmt = '{type}{block_group_id}{block_index}{drive_id}{block_id_seq:0>10}'
