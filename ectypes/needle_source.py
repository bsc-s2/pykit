#!/usr/bin/env python2
# coding: utf-8

from pykit.dictutil import FixedKeysDict
from referrer import Referrer


class NeedleSource(FixedKeysDict):

    # referrers must be added in non-descending order

    keys_default = dict((('NeedleID', str),
                         ('Referrers', list),
                         ('Size', int),
                         ('Url', str),))
    ident_keys = ('NeedleID',)

    def __init__(self, *args, **argkv):

        self.reserve_del = True

        super(NeedleSource, self).__init__(*args, **argkv)

    def __lt__(self, another):
        return self.ident() < another.ident()

    def add_referrer(self, referrer):

        # before the new referrers is added into the Referrers,the Referrers
        # are sorted fot they are imported from phy

        if not isinstance(referrer, Referrer):
            raise ValueError('referrer is not type Referrer')

        if len(self['Referrers']) > 1:

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
                return

        if not self.reserve_del and referrer['IsDel'] == 1:
            return

        self['Referrers'].append(referrer)

    def needle_id_equal(self, another):
        return self.ident() == another.ident()