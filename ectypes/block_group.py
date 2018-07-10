#!/usr/bin/env python2
# coding: utf-8

from collections import defaultdict

from pykit.dictutil import FixedKeysDict

from .block_desc import BlockDesc
from .block_group_id import BlockGroupID
from .block_index import BlockIndex
from .replication_config import ReplicationConfig


class BlockGroupBaseError(Exception):
    pass


class BlockNotFoundError(BlockGroupBaseError):
    pass


class BlockExists(BlockGroupBaseError):
    pass


class BlockTypeNotSupported(BlockGroupBaseError):
    pass


class BlockTypeNotSupportReplica(BlockGroupBaseError):
    pass


def _idcs(lst):
    return list(lst)


class BlockGroup(FixedKeysDict):

    keys_default = dict(
        block_group_id=BlockGroupID,
        config=ReplicationConfig,
        idcs=_idcs,
        blocks=dict,
    )

    ident_keys = ('block_group_id',)

    def __init__(self, *args, **kwargs):
        super(BlockGroup, self).__init__(*args, **kwargs)
        self.type_map = self.make_type_map()

    def get_block_type(self, block_index):

        mp = self.type_map
        bi = BlockIndex(block_index)

        try:
            return mp[bi.i][bi.j]
        except IndexError:
            raise BlockTypeNotSupported('invalid index at {bi}'.format(bi=bi))

    def make_type_map(self):

        cnf = self['config']

        nr_data, nr_parity = cnf['in_idc']
        nr_in_idc, nr_xor_idc = cnf['cross_idc']
        data_replica = cnf['data_replica']

        rst = []

        prefixes = ('d' * nr_in_idc
                    + 'x' * nr_xor_idc)

        for pref in prefixes:

            o = [pref + '0'] * nr_data
            o += [pref + 'p'] * nr_parity

            for j in range(1, data_replica):
                o += ['%s%d' % (pref, j)] * nr_data

            rst.append(o)

        return rst

    def mark_delete_block(self, block_index):
        block = self.get_block(block_index, raise_error=True)
        block['is_del'] = 1

    def delete_block(self, block_index):
        block = self.get_block(block_index)
        if block is not None:
            del self['blocks'][str(block_index)]

    def add_block(self, new_block, replace=False):

        desc = BlockDesc(new_block)
        bi = desc['block_id']

        bidx = str(bi.block_index)

        prev = self['blocks'].get(bidx)
        if not replace and prev is not None:
            raise BlockExists('there is already a block at {bi}'.format(bi=bi))

        self['blocks'][bidx] = desc

        if prev is None:
            return None
        else:
            return BlockDesc(prev)

    def get_free_block_indexes(self, block_type=None, get_all=False):

        free_block_index = defaultdict(list)

        cnf = self['config']
        n = sum(cnf['cross_idc'])
        m = sum(cnf['in_idc'])

        for i in range(n):
            for j in range(m):
                bi = BlockIndex(i, j)
                typ = self.get_block_type(bi)

                idc = self.get_block_idc(bi)

                if get_all:
                    # set the key 'idc' with default if key not set
                    free_block_index[idc]

                if block_type is not None and typ != block_type:
                    continue

                if self.get_block(bi) is None:
                    free_block_index[idc].append(str(bi))

        return free_block_index

    def get_block(self, block_index, raise_error=False):

        bi = BlockIndex(block_index)
        b = self['blocks'].get(str(bi))

        if raise_error and b is None:
            raise BlockNotFoundError(
                'block_index:{bi}'
                ' not found in block_group:{block_group_id}'.format(bi=bi, **self))

        return b

    def get_block_idc(self, block_index):

        bi = BlockIndex(block_index)

        return self['idcs'][bi.i]

    def get_primary_index(self, block_index):

        nr_data, nr_parity = self['config']['in_idc']

        bi = BlockIndex(block_index)

        j = bi.j
        if j >= nr_data:
            j -= nr_parity
            j %= nr_data

        return BlockIndex(bi.i, j)

    def get_replica_indexes(self, block_index, include_me=True):

        nr_data, nr_parity = self['config']['in_idc']
        data_replica = self['config']['data_replica']

        bi = BlockIndex(block_index)
        typ = self.get_block_type(bi)

        if typ.endswith('p'):
            raise BlockTypeNotSupportReplica(
                'block type {typ}'
                ' does not support replica'.format(typ=typ))

        pbi = self.get_primary_index(block_index)

        rst = [str(pbi)]

        for j in range(1, data_replica):
            rbi = BlockIndex(pbi.i,
                             pbi.j + nr_parity + j * nr_data)
            rst.append(str(rbi))

        # if not include_me and str(block_index) in rst:
        if not include_me:
            rst.remove(str(block_index))

        return rst

    def classify_blocks(self, idc_index, only_primary=True):

        nr_data, nr_parity = self['config']['in_idc']

        ec = []
        replica = []
        mark_del = []

        for i in range(0, nr_data):

            bi = BlockIndex(idc_index, i)

            blk = self.get_block(bi)
            if blk is None:
                continue

            if blk['is_del'] == 1:
                mark_del.append(blk)
                continue

            replica_idxes = self.get_replica_indexes(bi, include_me=False)
            rblks = self.indexes_to_blocks(replica_idxes)

            if None in rblks:
                ec.append(blk)
                continue

            replica.append(blk)
            if only_primary:
                continue

            replica.extend(rblks)

        return {'ec': ec, 'replica': replica, 'mark_del': mark_del}

    def indexes_to_blocks(self, indexes):

        blks = []

        for idx in indexes:
            bi = BlockIndex(idx)

            blk = self.get_block(bi)
            blks.append(blk)

        return blks

    def get_parity_indexes(self, idc_index):

        indexes = []
        nr_data, nr_parity = self['config']['in_idc']

        for i in range(nr_data, nr_data + nr_parity):

            bi = BlockIndex(idc_index, i)
            indexes.append(bi)

        return indexes

    def get_parities(self, idc_index):

        idxes = self.get_parity_indexes(idc_index)

        blks = self.indexes_to_blocks(idxes)

        return [blk for blk in blks if blk is not None]
