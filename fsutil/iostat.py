#!/usr/bin/env python2
# coding: utf-8

import shelve
import time

from pykit import config

from . import fsutil

MAJOR = 0
MINOR = 1
NAME = 2

READ_N = 3
READ_MERGED_N = 4
READ_SEC_N = 5
READ_MS = 6

WRITE_N = 7
WRITE_MERGED_N = 8
WRITE_SEC_N = 9
WRITE_MS = 10

IO_INPROC_N = 11
IO_MS = 12
IO_WEIGHTED_MS = 13

tmpl = {
    "name": NAME,
    "r": {
        "n": READ_N,
        "merge_n": READ_MERGED_N,
        "sec_n": READ_SEC_N,
        "ms": READ_MS,
    },
    "w": {
        "n": WRITE_N,
        "merge_n": WRITE_MERGED_N,
        "sec_n": WRITE_SEC_N,
        "ms": WRITE_MS,
    },
    "io": {
        "inproc_n": IO_INPROC_N,
        "ms": IO_MS,
        "weighted_ms": IO_WEIGHTED_MS,
    },
}


class DeviceNotFound(Exception):
    pass


def iostat(device=None, path=None, stat_path=None):

    # device: /dev/sdb*
    # path:   /home/guest
    # devname: sdb*
    #
    # returns {
    #   ioutil: 0-100 percentage
    #   read: Byte/s
    #   write: Byte/s
    # }

    assert device is not None or path is not None

    if stat_path is None:
        stat_path = config.iostat_stat_path

    if device is None:
        device = fsutil.get_device(path)

    devname = device.split('/', 2)[2]

    while True:
        curr = load_st(devname)
        prev = read_prev(stat_path, devname)

        if prev is None:
            write_prev(stat_path, devname, curr)
            time.sleep(1)
            continue

        duration = curr['ts'] - prev['ts']
        if curr['ts'] - prev['ts'] <= 0:
            write_prev(stat_path, devname, curr)
            time.sleep(1)
            continue

        if duration > 20:
            write_prev(stat_path, devname, curr)

        break

    st = {'ioutil': curr['io']['ms'] - prev['io']['ms'],
          'read':  curr['r']['byte'] - prev['r']['byte'],
          'write': curr['w']['byte'] - prev['w']['byte'],
          }
    for k, v in st.items():
        st[k] = v / duration

    # ioutil is recorded in millisecond
    st['ioutil'] = st['ioutil'] * 100 / 1000
    st['ioutil'] = min([100, st['ioutil']])

    return st


def read_prev(stat_path, devname):

    d = None
    try:
        d = shelve.open(stat_path)
        return d.get(devname)

    finally:
        if d is not None:
            d.close()


def write_prev(stat_path, devname, st):

    d = None
    try:
        d = shelve.open(stat_path)
        d[devname] = st

    finally:
        if d is not None:
            d.close()


def load_st(devname):

    sys_key = get_sys_key(devname)

    sts = fsutil.read_file('/proc/diskstats')
    lines = sts.strip().split("\n")

    elts = []
    for line in lines:
        elts = line.strip().split()
        if elts[NAME] == sys_key:
            break
    else:
        raise DeviceNotFound("device not found in /proc/diskstats: " + sys_key)

    sector_size = fsutil.read_file('/sys/block/{sys_key}/queue/hw_sector_size'.format(
        sys_key=sys_key))

    sector_size = int(sector_size)

    st = format_dev_st(elts, sector_size)
    st['name'] = devname
    return st


def get_sys_key(devname):

    if devname.startswith('mapper/'):
        # device on lvm.
        # /proc/diskstats use name "dm-*" for lvm disk
        lvs = get_all_lvs()
        n = lvs.index('/dev/' + devname)
        return 'dm-' + str(n)

    if devname.startswith('cciss/'):
        # cciss/c0d0p1
        return devname

    # NOTE: on some old OS, there is no 14 column for partition like
    # "/dev/sdb1", which is found on "218.30.114.74".
    if not devname.startswith('loop'):
        # //dev/loop2 has no parent dev
        return devname.rstrip('0123456789')

    return devname


def get_all_lvs():

    lvs = []

    maps = fsutil.read_file('/etc/mtab').strip()
    maps = maps.split('\n')

    for m in maps:
        m = m.strip()
        if m == "":
            continue

        nm = m.split()[0]
        if nm.startswith('/dev/mapper/'):
            lvs.append(nm)

    return lvs


def format_dev_st(elts, sector_size):

    st = {}

    for k, i in tmpl.items():
        if isinstance(i, int):
            if elts[i].isdigit():
                st[k] = int(elts[i])
            else:
                st[k] = elts[i]
        else:
            st[k] = {}
            for k2, j in tmpl[k].items():
                st[k][k2] = int(elts[j])

    st['ts'] = int(time.time())
    st['r']['byte'] = st['r']['sec_n'] * sector_size
    st['w']['byte'] = st['w']['sec_n'] * sector_size
    return st
