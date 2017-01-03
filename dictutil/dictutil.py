#!/bin/env python2
# coding: utf-8


def depth_iter(mydict, ks=None, maxdepth=10240, get_mid=False):

    ks = ks or []

    for k, v in mydict.items():

        ks.append(k)

        if len(ks) >= maxdepth:
            yield ks, v
        else:
            if isinstance(v, dict):

                if get_mid:
                    yield ks, v

                for _ks, v in depth_iter(v, ks, maxdepth=maxdepth,
                                         get_mid=get_mid):
                    yield _ks, v
            else:
                yield ks, v

        ks.pop(-1)


def breadth_iter(mydict):

    q = [([], mydict)]

    while True:
        if len(q) < 1:
            break

        _ks, node = q.pop(0)
        for k, v in node.items():
            ks = _ks[:]
            ks.append(k)
            yield ks, v

            if isinstance(v, dict):
                q.append((ks, v))
