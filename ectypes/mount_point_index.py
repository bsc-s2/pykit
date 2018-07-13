#!/usr/bin/env python2
# coding: utf-8


class MountPointIndex(str):

    def __new__(clz, s):

        if isinstance(s, int):
            s = '{s:0>3}'.format(s=s)

        if len(s) != 3 or not (0 <= int(s) <= 999):
            raise ValueError('invalid mount point index: {s}'.format(s=s))

        return super(MountPointIndex, clz).__new__(clz, s)
