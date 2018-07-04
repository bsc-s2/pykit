#!/usr/bin/env python
# coding: utf-8

from collections import namedtuple

from pykit.dictutil import FixedKeysDict

RSConfig = namedtuple('RSConfig', 'data,parity')


def _replica(n=None):
    # data_replica can not be smaller than 1
    if n is None:
        return 1

    n = int(n)
    if n < 1:
        raise ValueError('N.O. replica must >=1')

    return n


def _ec_policy(p=None):
    if p is None:
        return 'lrc'
    return str(p)


class ReplicationConfig(FixedKeysDict):

    keys_default = {
        'in_idc': lambda dp: RSConfig(dp[0], dp[1]),
        'cross_idc': lambda dp: RSConfig(dp[0], dp[1]),
        'ec_policy': _ec_policy,
        'data_replica': _replica,
    }
