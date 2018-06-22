#!/usr/bin/env python2
# coding: utf-8

import re
import socket
import uuid
from collections import defaultdict
from collections import namedtuple

import psutil

from pykit import fsutil
from pykit import net
from pykit import strutil

from .idbase import IDBase


class DriveIDError(Exception):
    pass


class ServerID(str):

    @classmethod
    def validate(cls, server_id):
        if not isinstance(server_id, basestring):
            return False

        return re.match("^[0-9a-f]{12}$", server_id) is not None

    @classmethod
    def local_server_id(self):
        return ServerID('%012x' % uuid.getnode())


class DriveID(namedtuple('_DriveID', 'server_id mountpoint_index'), IDBase):

    _tostr_fmt = '{server_id}0{mountpoint_index:0>3}'

    @classmethod
    def validate(cls, drive_id):
        if not isinstance(drive_id, basestring):
            return False

        if len(drive_id) != 16:
            return False

        server_id = drive_id[:12]
        padding = drive_id[12:13]
        mp_idx = drive_id[13:]

        return (ServerID.validate(server_id)
                and padding == '0'
                and re.match("^[0-9]{3}$", mp_idx) is not None)

    @classmethod
    def parse(cls, drive_id):
        if not DriveID.validate(drive_id):
            raise DriveIDError('invalid drive id: {d}'.format(d=drive_id))

        return DriveID(ServerID(drive_id[:12]),
                       int(drive_id[13:]))


def _make_mountpoints_info():
    mps = fsutil.get_all_mountpoint()
    prt_by_mp = fsutil.get_disk_partitions()

    mps_info = defaultdict(dict)
    for m in mps:
        p = prt_by_mp.get(m, None)
        if p is None:
            continue

        capacity = fsutil.get_path_usage(m)['total']

        mps_info[m]['fs'] = p['fstype']
        mps_info[m]['capacity'] = capacity

    return dict(mps_info)


def _get_allocated_drive(allocated_drive_pre, mountpoints):
    rst = {}
    for m in mountpoints:
        if not m.startswith(allocated_drive_pre):
            continue

        rst[m] = {'status': 'normal'}

    return rst


def make_serverrec(idc, idc_type, roles, allocated_drive_pre, **argkv):
    serverrec = {}

    ips = net.get_host_ip4(exclude_prefix="docker")
    inn_ips = net.choose_inn(ips)
    pub_ips = net.choose_pub(ips)

    memory = psutil.virtual_memory().total
    cpu_info = {}
    # count of logical cpus
    cpu_info['count'] = psutil.cpu_count()
    # Mhz
    if hasattr(psutil, 'cpu_freq'):
        cpu_info['frequency'] = psutil.cpu_freq().max

    serverrec['server_id'] = str(ServerID())
    serverrec['pub_ips'] = pub_ips
    serverrec['inn_ips'] = inn_ips
    serverrec['hostname'] = socket.gethostname()
    serverrec['memory'] = memory
    serverrec['cpu'] = cpu_info
    serverrec['idc'] = idc
    serverrec['idc_type'] = idc_type
    serverrec['roles'] = roles

    mps = _make_mountpoints_info()
    serverrec['mountpoints'] = mps
    serverrec['next_mount_index'] = 1
    serverrec['allocated_drive'] = _get_allocated_drive(allocated_drive_pre, mps)
    serverrec.update(argkv)

    return serverrec


def get_serverrec_str(serverrec):
    rst = []

    for k in ('server_id', 'idc', 'idc_type', 'roles'):
        rst.append('{k}: {v}'.format(k=k, v=serverrec[k]))

    rst.append('mountpoints_count: {cnt}'.format(
               cnt=len(serverrec['mountpoints'])))

    rst.append('allocated_drive_count: {cnt}'.format(
        cnt=len(serverrec['allocated_drive'])))

    return '; '.join(rst)


def validate_idc(idc):
    if not isinstance(idc, basestring):
        return False

    if len(idc) > 0 and not idc.startswith('.'):
        return False

    names = idc.split('.')
    for n in names:
        if re.match("^[0-9a-zA-Z]*$", n) is None:
            return False

    return True


def idc_distance(idc_a, idc_b):
    if idc_a == idc_b:
        return 0

    pre_cnt = len(strutil.common_prefix(idc_a.split('.'), idc_b.split('.')))
    return 32 / (2 ** pre_cnt)
