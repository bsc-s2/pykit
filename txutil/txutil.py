#!/usr/bin/env python
# coding: utf-8


import copy
import logging

logger = logging.getLogger(__name__)


class CASError(Exception):
    pass


class CASConflict(CASError):
    pass


class CASRecord(object):
    def __init__(self, v, stat, n):
        self.v = v
        self.stat = stat
        self.n = n


def cas_loop(getter, setter, args=(), kwargs=None, conflicterror=CASConflict):

    if kwargs is None:
        kwargs = {}

    i = -1
    while True:

        i += 1

        val, stat = getter(*args, **kwargs)
        rec = CASRecord(copy.deepcopy(val), stat, i)

        yield rec

        if rec.v == val:
            # nothing to update
            return

        try:
            setter(*(args + (rec.v, rec.stat)), **kwargs)
            return
        except conflicterror as e:
            logger.info(repr(e) + ' while cas set')
            continue
