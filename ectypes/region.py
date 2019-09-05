#!/usr/bin/env python
# coding: utf-8

import bisect

from pykit import rangeset
from pykit.dictutil import FixedKeysDict

from .block_id import BlockID

MERGE_COEF = 4


class BlockNotInRegion(Exception):
    pass


class BlockAreadyInRegion(Exception):
    pass


class LevelOutOfBound(Exception):
    pass


def _range(region_range=None):

    if region_range is not None:
        region_range = rangeset.Range(*region_range)

    return region_range


def _levels(levels=None):

    if levels is None:
        levels = []

    for level, range_bids in enumerate(levels):
        for b in range_bids:
            b[2] = BlockID(b[2])

        levels[level] = rangeset.RangeDict(range_bids)

    return levels


class Region(FixedKeysDict):

    keys_default = dict(
        idc=str,
        range=_range,
        levels=_levels,
    )

    def find_moved_to_level(self, src_block, src_level, region_levels):

        for level in reversed(range(src_level)):

            blocks = region_levels[level]
            overlapped = blocks.find_overlapped(src_block)

            if len(overlapped) != 0:
                level += 1
                return level

        return 0

    def move_down(self):

        region_levels = self['levels']
        moved_blocks = []

        for level, src_blocks in enumerate(region_levels):
            if level == 0:
                continue

            for src in src_blocks[:]:
                target_level = self.find_moved_to_level(
                    src, level, region_levels)
                if level == target_level:
                    continue

                moved_blocks.append((level, target_level, src))

                region_levels[level].remove(src)
                region_levels[target_level].add(src[:2], src[2])

        while len(region_levels) > 0 and region_levels[-1] == []:
            region_levels.pop(-1)

        return moved_blocks

    def list_block_ids(self, start_block_id=None):

        block_ids = []

        for blocks in self['levels']:
            level_bids = [b[2] for b in blocks]
            block_ids.extend(level_bids)

        block_ids.sort()

        if start_block_id is not None:
            start_block_id = BlockID(start_block_id)
            idx = bisect.bisect_left(block_ids, start_block_id)
            block_ids = block_ids[idx:]

        return block_ids

    def replace_block_id(self, block_id, new_block_id):
        block_id = BlockID(block_id)
        new_block_id = BlockID(new_block_id)

        for blocks in self['levels']:

            for block in blocks:
                if block[2] == block_id:
                    block[2] = new_block_id
                    return

        raise BlockNotInRegion('block_id: %s' % str(block_id))

    def delete_block(self, block_id, active_range=None, level=None, move=True):
        region_levels = self['levels']

        for lvl, level_blocks in enumerate(region_levels):

            if level is not None and level != lvl:
                continue

            for blk in level_blocks:

                if active_range is not None and active_range != blk[:2]:
                    continue

                if blk[2] == block_id:
                    level_blocks.remove(blk)
                    break
            else:
                continue

            if move and len(level_blocks) == 0:
                region_levels.pop(lvl)

            return

        raise BlockNotInRegion('block_id: {bid}'.format(bid=block_id))

    def add_block(self, active_range, block_id, level=None, allow_exist=False):

        if self.has(block_id):
            if not allow_exist:
                raise BlockAreadyInRegion('block_id {bid}'.format(bid=block_id))
            return

        max_level = len(self['levels']) - 1

        if level is None:
            level = max_level + 1

        elif level < 0 or level > max_level + 1:
            raise LevelOutOfBound('level is invalid. except level >= 0 and level <= {0}, '
                                  'got: {1}'.format(max_level + 1, level))

        if level == max_level + 1:
            self['levels'].append(rangeset.RangeDict())

        self['levels'][level].add(active_range, BlockID(block_id))

    def get_block_ids_by_needle_id(self, needle_id):

        region_range = self['range']
        levels = self['levels']

        if region_range is None:
            return []

        if not region_range.has(needle_id):
            return []

        rst = []

        for level in reversed(levels):

            try:
                block_id = level.get(needle_id)
            except KeyError:
                continue

            rst.append(block_id)

        return rst

    def has(self, block_id, active_range=None):
        for blocks in self['levels']:
            for blk in blocks:

                if active_range is not None and active_range != blk[:2]:
                    continue

                if blk[2] == block_id:
                    return True

        return False

    def get_block_byid(self, block_id, active_range=None, raise_error=True):
        for blocks in self['levels']:
            for blk in blocks:

                if active_range is not None and active_range != blk[:2]:
                    continue

                if blk[2] == block_id:
                    return blk

        if raise_error:
            raise BlockNotInRegion('block_id: %s' % str(block_id))

        return None
