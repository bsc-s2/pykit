#!/usr/bin/env python2
# coding: utf-8

IDC_ID_LEN = 6


class IDCID(str):

    def __new__(clz, s):
        s = str(s)
        if len(s) != IDC_ID_LEN:
            raise ValueError('IDCID length must be {l} but: {s!r}'.format(
                    l=IDC_ID_LEN, s=s))

        return super(IDCID, clz).__new__(clz, s)
