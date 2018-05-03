#!/usr/bin/env python2
# coding: utf-8

from collections import defaultdict
import psutil
import re
import socket
import uuid

from pykit import fsutil
from pykit import net
from pykit import strutil


def make_server_id():
    node = '%032x' % uuid.getnode()
    return node[-12:]


def validate_server_id(server_id):
    if not isinstance(server_id, basestring):
        return False

    return re.match("^[0-9a-f]{12}$", server_id) is not None


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


def make_serverrec(idc, idc_type, roles, **argkv):
    serverrec = {}

    ips = net.get_host_ip4()
    inn_ips = net.choose_inn(ips)
    pub_ips = net.choose_pub(ips)

    memory = psutil.virtual_memory().total
    cpu_info = {}
    # count of logical cpus
    cpu_info['count'] = psutil.cpu_count()
    # Mhz
    if hasattr(psutil, 'cpu_freq'):
        cpu_info['frequency'] = psutil.cpu_freq().max

    serverrec['server_id'] = make_server_id()
    serverrec['pub_ips'] = pub_ips
    serverrec['inn_ips'] = inn_ips
    serverrec['hostname'] = socket.gethostname()
    serverrec['memory'] = memory
    serverrec['cpu'] = cpu_info
    serverrec['idc'] = idc
    serverrec['idc_type'] = idc_type
    serverrec['roles'] = roles
    serverrec['mountpoints'] = _make_mountpoints_info()
    serverrec.update(argkv)

    return serverrec


def get_serverrec_str(serverrec):
    rst = []

    for k in ('server_id', 'idc', 'idc_type', 'roles'):
        rst.append('{k}: {v}'.format(k=k, v=serverrec[k]))

    rst.append('mountpoints_count: {cnt}'.format(
               cnt=len(serverrec['mountpoints'])))

    return '; '.join(rst)


def make_drive_id(server_id, mount_point_index):
    return '{sid}0{idx:0>3}'.format(
           sid=server_id,
           idx=mount_point_index % 1000)


def parse_drive_id(drive_id):
    server_id = drive_id[:12]
    mp_idx = int(drive_id[13:16])

    return {
        'server_id': server_id,
        'mount_point_index': mp_idx,
    }


def validate_drive_id(drive_id):
    if not isinstance(drive_id, basestring):
        return False

    if len(drive_id) != 16:
        return False

    server_id = drive_id[:12]
    padding = drive_id[12:13]
    mp_idx = drive_id[13:]

    return (validate_server_id(server_id)
            and padding == '0'
            and re.match("^[0-9]{3}$", mp_idx) is not None)


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
