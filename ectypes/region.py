#!/usr/bin/env python
# coding: utf-8

import bisect

from pykit import rangeset
from pykit.dictutil import FixedKeysDict

from .block_desc import BlockDesc
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

    for level, blocks in enumerate(levels):
        for b in blocks:
            b[2] = BlockDesc(b[2])

        levels[level] = rangeset.RangeDict(blocks)

    return levels


class Region(FixedKeysDict):

    keys_default = dict(
        idc=str,
        range=_range,
        levels=_levels,
    )

    def need_merge(self, source, targets):

        src_blk_size = source[2]['size']

        target_blk_size = 0
        for target in targets:
            target_blk_size += target[2]['size']

        return MERGE_COEF * src_blk_size >= target_blk_size

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

    def find_merge(self):

        region_levels = self['levels']

        for level, src_blocks in enumerate(region_levels):
            if level == 0:
                continue

            lower_blocks = region_levels[level - 1]

            for src in src_blocks:
                overlapped = lower_blocks.find_overlapped(src)

                if len(overlapped) == 0:
                    continue

                if self.need_merge(src, overlapped):
                    return (level, src, overlapped)

    def list_block_ids(self, start_block_id=None):

        block_ids = []

        for blocks in self['levels']:
            level_bids = [b[2]['block_id'] for b in blocks]
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
                if block[2]['block_id'] == block_id:
                    block[2]['block_id'] = new_block_id
                    return

        raise BlockNotInRegion('block_id: %s' % str(block_id))

    def delete_block(self, block, active_range=None, level=None, move=True):
        region_levels = self['levels']

        for lvl, level_blocks in enumerate(region_levels):

            if level is not None and level != lvl:
                continue

            for blk in level_blocks:

                if active_range is not None and active_range != blk[:2]:
                    continue

                if blk[2] == block:
                    level_blocks.remove(blk)
                    break
            else:
                continue

            if move and len(level_blocks) == 0:
                region_levels.pop(lvl)

            return

        raise BlockNotInRegion('block: {bi}'.format(bi=block))

    def add_block(self, active_range, block, level=None, allow_exist=False):

        if self.has(block):
            if not allow_exist:
                raise BlockAreadyInRegion('block {bi}'.format(bi=block))
            return

        max_level = len(self['levels']) - 1

        if level is None:
            level = max_level + 1

        elif level < 0 or level > max_level + 1:
            raise LevelOutOfBound('level is invalid. except level >= 0 and level <= {0}, '
                                  'got: {1}'.format(max_level + 1, level))

        if level == max_level + 1:
            self['levels'].append(rangeset.RangeDict())

        desc = BlockDesc(block)
        self['levels'][level].add(active_range, desc)

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
                block_desc = level.get(needle_id)
            except KeyError:
                continue

            rst.append(block_desc['block_id'])

        return rst

    def has(self, block, active_range=None):
        for blocks in self['levels']:
            for blk in blocks:

                if active_range is not None and active_range != blk[:2]:
                    continue

                if blk[2] == block:
                    return True

        return False
