#!/usr/bin/env python2
# coding: utf-8

from .server_id import ServerID
from .mount_point_index import MountPointIndex

from .idbase import IDBase

from pykit import config

def _padding_0(s):
    if str(s) != '0':
        raise ValueError('padding must be "0", but: {s}'.format(s=s))
    return str(s)

def _port(s):

    return config.ec_block_port + int(s)


class DriveID(IDBase):

    _attrs = (
        ('server_id', 0, 18, ServerID, 'embed'),
        ('_padding_0', 18, 19, _padding_0),
        ('mountpoint_index', 19, 22, MountPointIndex),
        ('port', 19 ,22, _port, False),

        ('drive_id', None, None, None, 'self'),
    )

    _str_len = 22

    _tostr_fmt = '{server_id}0{mountpoint_index:0>3}'
