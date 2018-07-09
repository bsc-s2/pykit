#!/usr/bin/env python
# coding: utf-8


from .idbase import IDBase


class BlockGroupID(IDBase):

    _attrs = (
        ('block_size', 1, 6, int),
        ('seq', 6, 16, int),
    )

    _str_len = 16

    _tostr_fmt = 'g{block_size:0>5}{seq:0>10}'
