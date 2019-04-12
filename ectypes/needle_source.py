#!/usr/bin/env python2
# coding: utf-8

import copy
import heapq

from pykit.dictutil import FixedKeysDict


class NeedleIdNotEqual(Exception):
    pass


class Referrer(FixedKeysDict):

    keys_default = dict((('Scope', str),
                         ('RefKey', str),
                         ('Ver', int),
                         ('IsDel', int),))
    ident_keys = ('Scope', 'RefKey', 'Ver', 'IsDel',)

    def __eq__(self, b):
        return self.ident() == b.ident()

    def __ne__(self, b):
        return self.ident() != b.ident()

    def __ge__(self, b):
        return self.ident() >= b.ident()

    def __gt__(self, b):
        return self.ident() > b.ident()

    def __le__(self, b):
        return self.ident() <= b.ident()

    def __lt__(self, b):
        return self.ident() < b.ident()

    def is_pair(self, b):
        a = self
        return (a.ident()[:3] == b.ident()[:3]
                and set([a['IsDel'], b['IsDel']]) == set([0, 1]))


def _referrer(refs=None):
    if refs is None:
        refs = []

    refs = [Referrer(r) for r in refs]
    return refs


class NeedleIdElt(FixedKeysDict):

    # referrers must be added in non-descending order

    keys_default = dict((('NeedleID', str),
                         ('Referrers', _referrer),
                         ('Size', int),
                         ('IsDel', int),
                         ('Meta', dict),
                         ('SysMeta', dict),))
    ident_keys = ('NeedleID',)

    def __init__(self, *args, **argkv):

        self.reserve_del = True
        super(NeedleIdElt, self).__init__(*args, **argkv)
        self.non_del_cnt = 0
        for referrer in self['Referrers']:
            if referrer['IsDel'] == 0:
                self.non_del_cnt += 1

    def needle_id_equal(self, another):
        return self.ident() == another.ident()

    def add_referrer(self, referrer):

        # before the new referrers are added into the Referrers, the Referrers
        # are sorted for they are corresponding to the phy

        if not isinstance(referrer, Referrer):
            raise ValueError('referrer is not type Referrer')

        if len(self['Referrers']) > 0:
            last_ref = self['Referrers'][-1]

            if referrer < last_ref:
                raise ValueError('referrer is not added in non-descending order')

            if last_ref.is_pair(referrer):
                if self.reserve_del:
                    ref = Referrer(self['Referrers'][-1])
                    ref['IsDel'] = 1
                    self['Referrers'][-1] = ref

                else:
                    del self['Referrers'][-1]

                self.non_del_cnt -= 1

                if self.non_del_cnt >= 1:
                    self['IsDel'] = 0
                else:
                    self['IsDel'] = 1

                return

        if not self.reserve_del and referrer['IsDel'] == 1:
            return

        self['Referrers'].append(referrer)

        if referrer['IsDel'] == 0:
            self.non_del_cnt += 1

        if self.non_del_cnt >= 1:
            self['IsDel'] = 0
        else:
            self['IsDel'] = 1


class NeedleSource(NeedleIdElt):

    keys_default = dict((('NeedleID', str),
                         ('Referrers', _referrer),
                         ('Size', int),
                         ('IsDel', int),
                         ('Meta', dict),
                         ('SysMeta', dict),
                         ('Url', str),
                         ('Level', int),))

    def __lt__(self, another):
        if another is None:
            return True
        elif isinstance(another, str):
            return ''.join(self.ident()) < another
        else:
            return self.ident() < another.ident()


def merge_referrer(needle_sources):

    merged_num = len(needle_sources)
    if merged_num == 0:
        return None

    sorted_needle_source = sorted(needle_sources, key=lambda needle_source: needle_source['Level'])

    needle_ids = [n['NeedleID'] for n in needle_sources]
    ndl_src = copy.deepcopy(needle_sources[0])

    if set(needle_ids) != set([ndl_src['NeedleID']]):
        raise NeedleIdNotEqual(needle_ids)

    refs = [n['Referrers'] for n in needle_sources]
    refs = heapq.merge(*refs)

    ndl_src['Referrers'] = []
    for ref in refs:
        ndl_src.add_referrer(ref)

    if len(ndl_src['Referrers']) > 0:

        ndl_src['Meta'] = sorted_needle_source[-1]['Meta']
        ndl_src['SysMeta'] = sorted_needle_source[-1]['SysMeta']
        ndl_src['Level'] = sorted_needle_source[0]['Level']

        return ndl_src
    else:
        return None


def merge_needle_source_iters(*needle_source_iters):

    ndl_src_iter = heapq.merge(*needle_source_iters)

    ndl_src_curr = ndl_src_iter.next()
    ndl_src_next = ndl_src_curr
    reserve_del = ndl_src_curr.reserve_del

    while True:

        merged_ndls = [ndl_src_curr]
        for ndl_src_next in ndl_src_iter:
            if ndl_src_curr.needle_id_equal(ndl_src_next):
                merged_ndls.append(ndl_src_next)
            else:
                break

        if reserve_del and len(merged_ndls) == 1:
            yield ndl_src_curr

        else:
            ndl_src = merge_referrer(merged_ndls)

            if ndl_src is not None:
                yield ndl_src

        if ndl_src_next == merged_ndls[-1]:
            break

        ndl_src_curr = ndl_src_next
