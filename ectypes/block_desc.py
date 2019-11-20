#!/usr/bin/env python2
# coding: utf-8
import time

from pykit import rangeset
from pykit.dictutil import FixedKeysDict

from .block_id import BlockID


def _block_id(block_id=None):

    if block_id is not None:
        block_id = BlockID(str(block_id))

    return block_id


def _range(block_range=None):

    if block_range is not None:
        block_range = rangeset.Range(*block_range)

    return block_range


def _is_del(is_del=0):

    if is_del not in (0, 1):
        raise ValueError(
            'block is_del should be 0 or 1, but {is_del}'.format(is_del=is_del))

    return is_del


def _mtime(ts=None):

    if ts is None:
        ts = time.time()

    return int(ts)


def _ts_range(ts_range=None):
    if ts_range is None:
        return ts_range

    if ts_range[0] is not None:
        ts_range[0] = str(ts_range[0])

    if ts_range[1] is not None:
        ts_range[1] = str(ts_range[1])

    return ts_range


class BlockDesc(FixedKeysDict):

    keys_default = dict(
        block_id=_block_id,
        size=int,
        range=_range,
        ts_range=_ts_range,
        is_del=_is_del,
        mtime=_mtime,
        ref_num=int,
    )

    def mark_del(self):
        if self['ref_num'] != 0:
            raise ValueError("cannot mark del block with ref_num:{n} > 0".format(
                n=self['ref_num']))

        self["is_del"] = 1
        self.mtime = int(time.time())

    def is_mark_del(self):
        return self['is_del'] == 1

    def add_ref(self):
        if self['is_del'] != 0:
            raise ValueError("reference a block marked delete")

        self['ref_num'] += 1

    def rm_ref(self):
        if self['ref_num'] < 1:
            raise ValueError("ref_num:{n} < 1".format(n=self['ref_num']))

        self['ref_num'] -= 1

    def can_del(self):
        return self['ref_num'] == 0
