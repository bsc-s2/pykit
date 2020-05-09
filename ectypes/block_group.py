#!/usr/bin/env python2
# coding: utf-8

import re

from collections import defaultdict

from pykit.dictutil import FixedKeysDict

from .block_id import BlockID
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


def _blocks(blocks=None):
    if blocks is None:
        return {}

    for idx, blk in blocks.items():
        blocks[idx] = BlockDesc(blk)

    return blocks


class BlockGroup(FixedKeysDict):

    keys_default = dict(
        block_group_id=BlockGroupID,
        config=ReplicationConfig,
        idcs=_idcs,
        blocks=_blocks,
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

        block.rm_ref()

        if block.can_del():
            block.mark_del()
            return block

        return None

    def mark_delete_block_byid(self, block_id):
        block = self.get_block_byid(block_id, raise_error=True)

        block.rm_ref()

        if block.can_del():
            block.mark_del()
            return block

        return None

    def unlink_block(self, block_index):
        block = self.get_block(block_index, raise_error=True)

        if not block.is_mark_del():
            block.rm_ref()

        if block.can_del():
            del self['blocks'][str(block_index)]
            return block

        return None

    def unlink_block_byid(self, block_id):
        block = self.get_block_byid(block_id, raise_error=True)

        if not block.is_mark_del():
            block.rm_ref()

        if block.can_del():
            del self['blocks'][block_id.block_index]
            return block

        return None

    def delete_block(self, block_index):
        return self.unlink_block(block_index)

    def delete_block_byid(self, block_id):
        return self.unlink_block_byid(block_id)

    def has(self, block):
        bid = block['block_id']
        bidx = bid.block_index

        existent = self['blocks'].get(bidx)
        return existent == block

    def link_block(self, block_index):
        block = self.get_block(block_index, raise_error=True)

        block.add_ref()
        return block

    def link_block_byid(self, block_id):
        block = self.get_block_byid(block_id, raise_error=True)

        block.add_ref()
        return block

    def add_block(self, new_block, replace=False, allow_exist=False):

        if self.has(new_block) and allow_exist:
            return new_block

        bid = new_block['block_id']
        bidx = bid.block_index

        prev = self['blocks'].get(bidx)
        if not replace and prev is not None:
            raise BlockExists(
                'there is already a block at {bid}'.format(bid=bid))

        self['blocks'][bidx] = new_block

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

                if self.get_block(bi, raise_error=False) is None:
                    free_block_index[idc].append(str(bi))

        return free_block_index

    def get_block(self, block_index, raise_error=True):

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

            blk = self.get_block(bi, raise_error=False)
            if blk is None:
                continue

            if blk.is_mark_del():
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

            blk = self.get_block(bi, raise_error=False)
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

    def is_ec_block(self, block_id):
        block_id = BlockID(block_id)

        blk = self.get_block(block_id.block_index, raise_error=False)
        if blk is None or blk['block_id'] != block_id:
            raise BlockNotFoundError(
                'block_id:{bid}'
                ' not found in block_group:{block_group_id}'.format(bid=block_id, **self))

        if block_id.type.endswith('p'):
            blk = self.get_block(block_id.block_index, raise_error=True)
            return True

        r_indexes = self.get_replica_indexes(block_id.block_index)
        r_blks = [self.get_block(x, raise_error=False) for x in r_indexes]

        return None in r_blks

    def get_blocks(self):
        blks = []

        for idx in sorted(self['blocks'].keys()):
            blk = self['blocks'][idx]
            blks.append(blk)

        return blks

    def get_ec_blocks(self, idc_idx):
        nr_data, nr_parity = self['config']['in_idc']

        blks = []
        for i in range(0, nr_data + nr_parity):
            blk = self.get_block(BlockIndex(idc_idx, i), raise_error=False)

            if blk is None:
                continue

            if self.is_ec_block(blk['block_id']):
                blks.append(blk)

        return blks

    def get_ec_broken_blocks(self, idc_idx, broken_bids):
        broken_blks = []

        for blk in self.get_ec_blocks(idc_idx):
            if blk['block_id'] in broken_bids:
                broken_blks.append(blk)

        return broken_blks

    def get_ec_block_ids(self, idc_idx):
        bids = []

        for blk in self.get_ec_blocks(idc_idx):
            bids.append(blk['block_id'])

        return bids

    def get_replica_blocks(self, block_id, include_me=True, raise_error=True):
        block_id = BlockID(block_id)
        r_indexes = self.get_replica_indexes(block_id.block_index, True)

        is_exist = False

        blks = []
        for idx in r_indexes:
            blk = self.get_block(idx, raise_error=False)

            if blk is None:
                continue

            if blk['block_id'] == block_id:
                is_exist = True

                if not include_me:
                    continue

            blks.append(blk)

        if not is_exist:
            if raise_error:
                raise BlockNotFoundError(self['block_group_id'], block_id)
            else:
                return None

        return blks

    def get_block_byid(self, block_id, raise_error=True):
        block_id = BlockID(block_id)

        blk = self.get_block(block_id.block_index, raise_error=False)
        if blk is None or blk['block_id'] != block_id:
            if raise_error:
                raise BlockNotFoundError(self['block_group_id'], block_id)
            else:
                return None

        return blk

    def get_idc_blocks(self, idc_idx, is_del=None, types=None):
        blks = []

        for idx in sorted(self['blocks'].keys()):
            blk = self['blocks'][idx]

            idx = BlockIndex(idx)
            typ = self.get_block_type(idx)

            if types is not None and typ not in types:
                continue

            if idx.i != idc_idx:
                continue

            if is_del is not None and blk['is_del'] != is_del:
                continue

            blks.append(blk)

        return blks

    def get_idc_blocks_no_replica(self, idc_idx, is_del=None):
        types = ['d0', 'dp', 'x0', 'xp']
        return self.get_idc_blocks(idc_idx, is_del=is_del, types=types)

    def get_d0_idcs(self):
        cross_idc = self["config"]["cross_idc"]
        return self["idcs"][:cross_idc[0]]

    def get_dtype_by_idc(self, idc):
        cfg = self["config"]

        assert idc in self["idcs"]
        assert sum(cfg["cross_idc"]) == len(self["idcs"])

        d0_idcs = self["idcs"][:cfg["cross_idc"][0]]

        if idc in d0_idcs:
            return "d0"
        else:
            return "x0"

    def get_idc_block_ids(self, idc_idx, is_del=None, types=None):
        blks = self.get_idc_blocks(idc_idx, is_del=is_del, types=types)
        return [BlockID(b['block_id']) for b in blks]

    def get_idc_block_ids_no_replica(self, idc_idx, is_del=None):
        types = ['d0', 'dp', 'x0', 'xp']
        return self.get_idc_block_ids(idc_idx, is_del=is_del, types=types)

    @classmethod
    def is_data(cls, block_id):
        return block_id.type in ('d0', 'x0')

    @classmethod
    def is_replica(cls, block_id):
        return re.match(r'd[1-9]', block_id.type) is not None

    @classmethod
    def is_parity(cls, block_id):
        return block_id.type in ('dp', 'xp')
