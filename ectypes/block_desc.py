#!/usr/bin/env python2
# coding: utf-8

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


class BlockDesc(FixedKeysDict):

    keys_default = dict(
        block_id=_block_id,
        size=int,
        range=_range,
        is_del=_is_del,
    )
