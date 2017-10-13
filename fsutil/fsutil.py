#!/usr/bin/env python2
# coding: utf-8

import binascii
import errno
import hashlib
import os
import time

import psutil

from pykit import config
from pykit import timeutil

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


def write_file(path, fcont, uid=None, gid=None, atomic=False):

    if not atomic:
        return _write_file(path, fcont, uid, gid)

    tmp_path = '{path}._tmp_.{pid}_{timestamp}'.format(
        path=path,
        pid=os.getpid(),
        timestamp=timeutil.ns(),
    )
    _write_file(tmp_path, fcont, uid, gid)

    try:
        os.rename(tmp_path, path)
    except EnvironmentError:
        os.remove(tmp_path)
        raise


def _write_file(path, fcont, uid=None, gid=None):

    uid = uid or config.uid
    gid = gid or config.gid

    with open(path, 'w') as f:
        f.write(fcont)
        f.flush()
        os.fsync(f.fileno())

    if uid is not None and gid is not None:
        os.chown(path, uid, gid)


def calc_checksums(path, sha1=False, md5=False, crc32=False,
                   block_size=READ_BLOCK, io_limit=READ_BLOCK):

    checksums = {
        'sha1': None,
        'md5': None,
        'crc32': None,
    }

    if (sha1 or md5 or crc32) is False:
        return checksums

    if block_size <= 0:
        raise FSUtilError('block_size must be positive integer')

    if io_limit == 0:
        raise FSUtilError('io_limit shoud not be zero')

    min_io_time = float(block_size) / io_limit

    sum_sha1 = hashlib.sha1()
    sum_md5 = hashlib.md5()
    sum_crc32 = 0

    with open(path, 'rb') as f_path:

        while True:
            t0 = time.time()

            buf = f_path.read(block_size)
            if buf == '':
                break

            t1 = time.time()

            time_sleep = max(0, min_io_time - (t1 - t0))
            if time_sleep > 0:
                time.sleep(time_sleep)

            if sha1:
                sum_sha1.update(buf)
            if md5:
                sum_md5.update(buf)
            if crc32:
                sum_crc32 = binascii.crc32(buf, sum_crc32)

    if sha1:
        checksums['sha1'] = sum_sha1.hexdigest()
    if md5:
        checksums['md5'] = sum_md5.hexdigest()
    if crc32:
        checksums['crc32'] = '%08x' % (sum_crc32 & 0xffffffff)

    return checksums


def _to_dict(_namedtuple):
    return dict(_namedtuple._asdict())
