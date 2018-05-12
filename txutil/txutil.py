#!/usr/bin/env python
# coding: utf-8


import copy
import logging

logger = logging.getLogger(__name__)


class CASRecord(object):
    def __init__(self, v, stat):
        self.v = v
        self.stat = stat


def cas_loop(getter, setter, key=None):

    while True:

        val, stat = getter(key)
        rec = CASRecord(copy.deepcopy(val), stat)

        yield rec

        if rec.v == val:
            # nothing to update
            return

        ok = setter(key, rec.v, rec.stat)
        if ok:
            return
