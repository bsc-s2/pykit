#!/usr/bin/env python2
# coding: utf-8

import copy
from collections import defaultdict

from .block import BlockID
from .block_index import BlockIndex
from .block_index import BlockIndexError

BlockIndexLen = 4


class BlockGroupBaseError(Exception):
    pass


class BlockNotFoundError(BlockGroupBaseError):
    pass


class BlockTypeNotSupported(BlockGroupBaseError):
    pass


class BlockTypeNotSupportReplica(BlockGroupBaseError):
    pass


class BlockGroup(dict):

    def __init__(self, block_group=None, **kwargs):

        if block_group is not None:
            self.update(copy.deepcopy(block_group))

        self.update(copy.deepcopy(kwargs))

    @classmethod
    def make(cls, block_group_id, idcs, config):

        bg = cls({
            'block_group_id': block_group_id,
            'bg_seq': 0,
            'config': copy.deepcopy(config),
            'idcs': idcs,
            'blocks': {}
        })

        nr_data, nr_parity = bg['config']['ec']['in_idc']

        for idc_idx, idc in enumerate(idcs):
            for pos in range(nr_data + nr_parity):
                b_idx = BlockIndex(idc_idx, pos)
                bg['blocks'][str(b_idx)] = bg.empty_block(b_idx)

        return bg

    def get_block_type(self, block_index):

        mp = self.get_type_map()
        bi = BlockIndex.parse(str(block_index))

        try:
            return mp[bi.i][bi.j]
        except IndexError:
            # TODO refine error
            raise BlockTypeNotSupported('type x{1~n} is not supported')

    def get_type_map(self):

        cnf = self['config']['ec']

        nr_data, nr_parity = cnf['in_idc']
        nr_in_idc, nr_xor_idc = cnf['cross_idc']
        data_replica = cnf['data_replica']

        rst = []

        for i in range(nr_in_idc):

            o = ['d0'] * nr_data + ['dp'] * nr_parity

            for ii in range(data_replica - 1):
                o += ['d%d' % (ii+1)] * nr_data

            rst.append(o)

        for i in range(nr_xor_idc):
            o = ['x0'] * nr_data + ['xp'] * nr_parity
            rst.append(o)

        return rst

    def empty_block(self, block_index):

        blk_type = self.get_block_type(block_index)

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

        self['blocks'][str(block_index)] = new_block

    def get_free_block_indexes(self, block_type=None):

        free_block_index = defaultdict(list)

        for b_idx, block in self['blocks'].items():

            if block_type is not None:
                if block['type'] != block_type:
                    continue

            if block['block_id'] is None:
                idc = self.get_block_idc(block_index=b_idx)
                free_block_index[idc].append(b_idx)

        for idc in free_block_index.keys():
            free_block_index[idc].sort()

        return free_block_index

    def get_block(self, block_index=None, block_id=None, raise_error=False):

        block = None

        if block_index is not None:
            msg = ('block_index:{i} '
                   'not found in block_group:{block_group_id}').format(i=block_index,
                                                                       **self)
            block_index = BlockIndex.parse(str(block_index))
            block = self['blocks'].get(str(block_index))

        elif block_id is not None:
            msg = ('block_id:{i} '
                   'not found in block_group:{block_group_id}').format(i=block_id,
                                                                       **self)

            block_index = BlockID.parse(block_id).block_index
            block = self['blocks'].get(str(block_index))

            if block is not None and block['block_id'] != block_id:
                block = None

        if raise_error is True and block is None:
            raise BlockNotFoundError(msg)

        return block_index, block

    def get_block_idc(self, block_index=None, block_id=None):

        blk_idx, _ = self.get_block(block_index=block_index,
                                    block_id=block_id,
                                    raise_error=True)

        return self['idcs'][blk_idx.i]

    def get_replica_block_index(self, block_index=None, block_id=None):

        if block_id is not None:
            bi, _ = self.get_block(block_id=block_id, raise_error=True)
        else:
            bi = BlockIndex.parse(str(block_index))

        blk_type = self.get_block_type(bi)

        if blk_type.endswith('p') or blk_type.startswith('x'):
            raise BlockTypeNotSupportReplica(('block type {0} '
                                              'do not support replica').format(blk_type))

        replica_block_index = []

        for rbi in self.get_replica_indexes(bi):
            if rbi.j == bi.j:
                continue

            replica_block_index.append(str(rbi))

        return replica_block_index

    def get_primary_index(self, block_index):

        nr_data, nr_parity = self['config']['ec']['in_idc']

        bi = BlockIndex.parse(str(block_index))

        j = bi.j
        if j >= nr_data:
            j -= nr_parity
            j %= nr_data

        return BlockIndex(bi.i, j)

    def get_replica_indexes(self, block_index):

        nr_data, nr_parity = self['config']['ec']['in_idc']
        data_replica = self['config']['ec']['data_replica']

        bi = self.get_primary_index(block_index)

        rst = [bi]

        for j in range(1, data_replica):
            rst.append(BlockIndex(bi.i,
                                  bi.j + nr_parity + j * nr_data))

        return rst
