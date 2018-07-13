#!/usr/bin/env python2
# coding: utf-8

from .server_id import ServerID
from .mount_point_index import MountPointIndex

from .idbase import IDBase


def _padding_0(s):
    if str(s) != '0':
        raise ValueError('padding must be "0", but: {s}'.format(s=s))
    return str(s)


class DriveID(IDBase):

    _attrs = (
        ('server_id', 0, 12, ServerID),
        ('_padding_0', 12, 13, _padding_0),
        ('mountpoint_index', 13, 16, MountPointIndex),
    )

    _str_len = 16

    _tostr_fmt = '{server_id}0{mountpoint_index:0>3}'
