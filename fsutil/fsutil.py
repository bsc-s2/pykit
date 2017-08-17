#!/usr/bin/env python2
# coding: utf-8

import errno
import os

import psutil

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
    mps = [x.mountpoint for x in partitions]
    return mps


def get_mountpoint(path):

    path = os.path.realpath(path)

    while not os.path.ismount(path):
        path = os.path.dirname(path)

    return path


def get_device(path):

    prt_by_mountpoint = get_disk_partitions()

    mp = get_mountpoint(path)

    return prt_by_mountpoint[mp]['device']


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


def makedirs(*paths, **kwargs):
    mode = kwargs.get('mode', 0755)
    uid = kwargs.get('uid')
    gid = kwargs.get('gid')

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
    with open(path, 'w') as f:
        f.write(fcont)
        f.flush()
        os.fsync(f.fileno())

    if uid is not None and gid is not None:
        os.chown(path, uid, gid)


def _to_dict(_namedtuple):
    return dict(_namedtuple._asdict())
