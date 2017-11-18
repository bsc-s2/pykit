#!/usr/bin/env python2
# coding: utf-8

import types

K = 1024 ** 1
M = 1024 ** 2
G = 1024 ** 3
T = 1024 ** 4
P = 1024 ** 5
E = 1024 ** 6
Z = 1024 ** 7
Y = 1024 ** 8

value_to_unit = {
    1: '',
    K: 'K',
    M: 'M',
    G: 'G',
    T: 'T',
    P: 'P',
    E: 'E',
    Z: 'Z',
    Y: 'Y',
}

unit_to_value = dict([(v, k)
                      for (k, v) in value_to_unit.items()
                      if v != ''
                      ])

integer_types = (type(0), type(0L))


def humannum_int(i, unit=None):

    i = int(i)

    if unit is None:

        unit = K

        # keep at least 2 digit
        while i / unit > 0:
            unit *= K

        unit /= K

        while unit not in value_to_unit:
            unit /= K

    v = i * 1.0 / unit

    if v == int(v):
        return '%d%s' % (v, value_to_unit[unit])

    if v > 10:
        vlen = 1
    elif v > 1:
        vlen = 2
    else:
        vlen = 3

    return ('%.' + str(vlen) + 'f%s') % (v, value_to_unit[unit])


def humannum(data, unit=None, include=None, exclude=None):

    if isinstance(data, types.DictType):

        data = data.copy()

        keys = set(data.keys())
        if include is not None:
            keys = keys & set(include)

        if exclude is not None:
            keys = keys - set(exclude)

        for k in keys:
            data[k] = humannum(data[k])

        return data

    elif isinstance(data, types.BooleanType):
        # We have to deal with bool because for historical reason bool is
        # subclass of int.
        # When bool is introduced into python 2.2 it is represented with int,
        # similar to C.
        return data

    elif isinstance(data, types.ListType):
        return [humannum(x) for x in data]

    elif isinstance(data, types.StringTypes):
        return data

    elif isinstance(data, integer_types):
        return humannum_int(data, unit=unit)

    elif isinstance(data, types.FloatType):
        if data > 999:
            return humannum_int(int(data), unit=unit)
        elif abs(data) < 0.0000000001:
            return '0'
        else:
            return '%.2f' % (data)

    else:
        return data


def parseint(data, safe=None):
    return int(parsenum(data, safe=safe))


def parsenum(data, safe=None):

    if safe is None:
        safe = False

    original = data

    if isinstance(data, integer_types):
        return data

    if not isinstance(data, types.StringTypes):
        return data

    if data == '':
        return 0

    if data.endswith('%'):
        fl = float(data[:-1]) / 100.0
        return fl

    data = data.upper().rstrip('B').rstrip('I')

    unit_name = data[-1]

    try:
        if unit_name in unit_to_value:
            val = float(data[:-1]) * unit_to_value[unit_name]
        else:
            val = float(data)

        if val == int(val):
            val = int(val)

    except ValueError:
        if safe:
            val = original
        else:
            raise

    return val
