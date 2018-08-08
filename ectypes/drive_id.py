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
        ('server_id', 0, 18, ServerID),
        ('_padding_0', 18, 19, _padding_0),
        ('mountpoint_index', 19, 22, MountPointIndex),
    )

    _str_len = 22

    _tostr_fmt = '{server_id}0{mountpoint_index:0>3}'
