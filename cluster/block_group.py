#!/usr/bin/env python2
# coding: utf-8

import copy

from collections import namedtuple
from collections import defaultdict
from .block import BlockID

BlockGroupIDLen = 16


class BlockGroupBaseError(Exception):
    pass


class BlockGroupIDError(BlockGroupBaseError):
    pass


class BlockNotFoundError(BlockGroupBaseError):
    pass


class BlockTypeNotSupported(BlockGroupBaseError):
    pass


class BlockGroupID(namedtuple('_BlockGroupID', 'block_size seq')):
    @classmethod
    def parse(cls, block_group_id):
        if len(block_group_id) != BlockGroupIDLen:
            raise BlockGroupIDError('Block group id length should be {0}, but is {1}: {2}'.format(
                BlockGroupIDLen, len(block_group_id), block_group_id))

        size = int(block_group_id[1:6])
        seq = int(block_group_id[6:])

        return BlockGroupID(size, seq)

    def __str__(self):
        blk_size = '%05d' % self.block_size
        seq = '%010d' % self.seq

        return 'g' + blk_size + seq

    def tostr(self):
        return str(self)


class BlockGroup(dict):
    @classmethod
    def make(cls, block_group_id, idcs, config):

        bg = cls({
            'block_group_id': block_group_id,
            'pg_seq': 0,
            'config': copy.deepcopy(config),
            'idcs': idcs,
            'blocks': {}
        })

        nr_data, nr_parity = bg['config']['ec']['in_idc']

        for idc_idx, idc in enumerate(idcs):
            for pos in range(nr_data + nr_parity):
                b_idx = '%02d%02d' % (idc_idx, pos)
                bg['blocks'][b_idx] = bg.empty_block(b_idx)

        return bg

    def calc_block_type(self, block_index):
        nr_data, nr_parity = self['config']['ec']['in_idc']
        nr_in_idc, nr_xor_idc = self['config']['ec']['cross_idc']

        idc_idx = int(block_index[:2])
        pos = int(block_index[2:])

        if idc_idx < nr_in_idc:

            if pos < nr_data:
                blk_type = 'd0'
            elif pos < nr_data + nr_parity:
                blk_type = 'dp'
            else:
                base_idx = (pos - nr_parity) / nr_data
                blk_type = 'd' + str(base_idx)
        else:

            if pos < nr_data:
                blk_type = 'x0'
            elif pos < nr_data + nr_parity:
                blk_type = 'xp'
            else:
                raise BlockTypeNotSupported('type x{1~n} is not supported')

        return blk_type

    def empty_block(self, block_index):
        blk_type = self.calc_block_type(block_index)

        block = {
            'block_id': None,
            'size': 0,
            'type': blk_type,
            'range': [None, None],
            'is_del': 1
        }

        return block

    def mark_delete_block(self, block_index=None, block_id=None):
        block_index, block = self.get_block(block_index=block_index,
                                            block_id=block_id,
                                            raise_error=True)
        block['is_del'] = 1

    def replace_block(self, new_block, block_index=None, block_id=None):
        block_index, block = self.get_block(block_index=block_index,
                                            block_id=block_id,
                                            raise_error=True)

        self['blocks'][block_index] = new_block

    def get_free_block_index(self, block_type=None):
        free_block_index = defaultdict(list)

        for b_idx, block in self['blocks'].items():

            if block_type is not None:
                if block['type'] != block_type:
                    continue

            if block['block_id'] is None:
                idc_idx = b_idx[0:2]
                idc = self['idcs'][int(idc_idx)]
                free_block_index[idc].append(b_idx)

        for idc in free_block_index.keys():
            free_block_index[idc].sort()

        return free_block_index

    def get_block(self, block_index=None, block_id=None, raise_error=False):
        block = None

        msg = ('block_index:{i} '
               'not found in block_group:{block_group_id}').format(i=block_index,
                                                                   **self)

        if block_index is not None:
            block = self['blocks'].get(block_index)

        elif block_id is not None:
            msg = ('block_id:{i} '
                   'not found in block_group:{block_group_id}').format(i=block_id,
                                                                       **self)

            block_index = BlockID.parse(block_id).block_index
            block = self['blocks'].get(block_index)
            if block['block_id'] != block_id:
                block = None

        if raise_error is True and block is None:
            raise BlockNotFoundError(msg)

        return block_index, block
