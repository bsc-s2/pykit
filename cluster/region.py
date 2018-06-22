#!/usr/bin/env python
# coding: utf-8

import copy

from pykit import rangeset


class Region(dict):

    fields_default = {'idc': None,
                      'range': [None, None],
                      'levels': [], }

    def __init__(self, region=None, **argkv):

        self.update(copy.deepcopy(self.fields_default))

        if region is not None:
            self.update(copy.deepcopy(region))

        self.update(copy.deepcopy(argkv))

        self['range'] = rangeset.Range(*self['range'])

        for level, blocks in enumerate(self['levels']):
            self['levels'][level] = rangeset.RangeDict(blocks)

    def need_merge(self, source, targets):

        src_blk_size = source[2]['size']

        target_blk_size = 0
        for target in targets:
            target_blk_size += target[2]['size']

        return 4 * src_blk_size >= target_blk_size

    def find_target_level(self, src_block, src_level, region_levels):

        for level in reversed(range(src_level)):

            blocks = region_levels[level]
            overlapped = blocks.find_overlapped(src_block)

            if len(overlapped) != 0:
                level += 1
                break

        return level

    def move_down(self):

        region_levels = self['levels']
        moved_blocks = []

        for level, src_blocks in enumerate(region_levels):
            if level == 0:
                continue

            for src in src_blocks[:]:
                target_level = self.find_target_level(
                    src, level, region_levels)
                if level == target_level:
                    continue

                moved_blocks.append((level, target_level, src))

                region_levels[level].remove(src)
                region_levels[target_level].add(src[:2], src[2])

        while region_levels[-1] == []:
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
