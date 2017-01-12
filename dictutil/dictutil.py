#!/bin/env python2
# coding: utf-8


def depth_iter(mydict, ks=None, maxdepth=10240, intermediate=False):

    ks = ks or []

    for k, v in mydict.items():

        ks.append(k)

        if len(ks) >= maxdepth:
            yield ks, v
        else:
            if isinstance(v, dict):

                if intermediate:
                    yield ks, v

                for _ks, v in depth_iter(v, ks, maxdepth=maxdepth,
                                         intermediate=intermediate):
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


def make_getter_str(code, default=0):

    s = 'lambda dic, vars={}: dic'

    entries = code.split('.')
    if entries == ['']:
        return s

    for e in entries:

        if e.startswith('$'):

            dynamic_key = 'str(vars.get("%s", "_"))' % (e[1:], )

            s += '.get(%s, {})' % (dynamic_key, )

        else:
            s += '.get("%s", {})' % (e, )

    s = s[:-3] + 'vars.get("_default", ' + repr(default) + '))'

    return s


def make_getter(code, default=0):
    return eval(make_getter_str(code, default=default))
