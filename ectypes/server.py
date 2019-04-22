#!/usr/bin/env python2
# coding: utf-8

import re
import socket
from collections import defaultdict

import psutil

from pykit import fsutil
from pykit import net
from pykit import strutil


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
    max_mount_idx = 0
    for m in mountpoints:
        if not m.startswith(allocated_drive_pre):
            continue

        rst[m] = {'status': 'normal'}
        idx = int(m.split('/')[-1])

        max_mount_idx = max_mount_idx if max_mount_idx > idx else idx

    return rst, max_mount_idx


def make_serverrec(server_id, idc, idc_type, roles, allocated_drive_pre, **argkv):
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

    serverrec['server_id'] = server_id
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
    allocated_drive, max_mount_idx = _get_allocated_drive(allocated_drive_pre, mps)
    serverrec['next_mount_index'] = max_mount_idx + 1
    serverrec['allocated_drive'] = allocated_drive
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

    # deprecated, use IDCID(idc)

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
