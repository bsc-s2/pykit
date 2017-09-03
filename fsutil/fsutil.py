#!/usr/bin/env python2
# coding: utf-8

import errno
import os

import psutil

from pykit import config

READ_BLOCK = 32 * 1024 * 1024
WRITE_BLOCK = 32 * 1024 * 1024


class FSUtilError(Exception):
    pass


class NotMountPoint(FSUtilError):
    pass


def assert_mountpoint(path):
    if not os.path.ismount(path):
        raise NotMountPoint(path)


def get_all_mountpoint(all=False):
    partitions = psutil.disk_partitions(all=all)
    prt_by_mp = [x.mountpoint for x in partitions]
    return prt_by_mp


def get_mountpoint(path):

    path = os.path.realpath(path)

    prt_by_mountpoint = get_disk_partitions()

    while path != '/' and path not in prt_by_mountpoint:
        path = os.path.dirname(path)

    return path


def get_device(path):

    prt_by_mountpoint = get_disk_partitions()

    mp = get_mountpoint(path)

    return prt_by_mountpoint[mp]['device']


def get_device_fs(device):

    prt_by_mp = get_disk_partitions()

    for prt in prt_by_mp.values():
        if device == prt['device']:
            return prt['fstype']
    else:
        return 'unknown'


def get_disk_partitions():

    partitions = psutil.disk_partitions(all=True)

    by_mount_point = {}
    for pt in partitions:
        # OrderedDict([
        #      ('device', '/dev/disk1'),
        #      ('mountpoint', '/'),
        #      ('fstype', 'hfs'),
        #      ('opts', 'rw,local,rootfs,dovolfs,journaled,multilabel')])
        by_mount_point[pt.mountpoint] = _to_dict(pt)

    return by_mount_point


def get_path_fs(path):

    mp = get_mountpoint(path)
    prt_by_mp = get_disk_partitions()

    return prt_by_mp[mp]['fstype']


def get_path_usage(path):

    space_st = os.statvfs(path)

    # f_bavail: without blocks reserved for super users
    # f_bfree:  with    blocks reserved for super users
    avail = space_st.f_frsize * space_st.f_bavail

    capa = space_st.f_frsize * space_st.f_blocks
    used = capa - avail

    return {
        'total': capa,
        'used': used,
        'available': avail,
        'percent': float(used) / capa,
    }


def makedirs(*paths, **kwargs):
    mode = kwargs.get('mode', 0755)
    uid = kwargs.get('uid') or config.uid
    gid = kwargs.get('gid') or config.gid

    path = os.path.join(*paths)

    # retry to deal with concurrent check-and-then-set issue
    for ii in range(2):

        if os.path.isdir(path):

            if uid is not None and gid is not None:
                os.chown(path, uid, gid)

            return

        try:
            os.makedirs(path, mode=mode)
            if uid is not None and gid is not None:
                os.chown(path, uid, gid)
        except OSError as e:
            if e.errno == errno.EEXIST:
                # concurrent if-exist and makedirs
                pass
            else:
                raise
    else:
        raise


def read_file(path):
    with open(path, 'r') as f:
        return f.read()


def write_file(path, fcont, uid=None, gid=None):

    uid = uid or config.uid
    gid = gid or config.gid

    with open(path, 'w') as f:
        f.write(fcont)
        f.flush()
        os.fsync(f.fileno())

    if uid is not None and gid is not None:
        os.chown(path, uid, gid)


def _to_dict(_namedtuple):
    return dict(_namedtuple._asdict())
