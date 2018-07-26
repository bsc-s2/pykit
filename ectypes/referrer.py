#!/usr/bin/ env python2
# coding: utf-8

from pykit.dictutil import FixedKeysDict


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
