#!/usr/bin/env python2
# coding: utf-8

from .server_id import ServerID
from .server import MountPointIndex
from .server import _padding_0

from .idbase import IDBase


class DriveID(IDBase):

    _attrs = (
        ('server_id', 0, 12, ServerID),
        ('_padding_0', 12, 13, _padding_0),
        ('mountpoint_index', 13, 16, MountPointIndex),
    )

    _str_len = 16

    _tostr_fmt = '{server_id}0{mountpoint_index:0>3}'
