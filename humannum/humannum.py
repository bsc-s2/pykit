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

unit_to_name = {
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
                      for (k, v) in unit_to_name.items()
                      if v != ''
                      ])


def humannum_int(i, unit=None):

    i = int(i)

    if unit is None:

        unit = K

        # keep at least 2 digit
        while i / unit > 0:
            unit *= K

        unit /= K

        while unit not in unit_to_name:
            unit /= K

    v = i * 1.0 / unit

    if v == int(v):
        return '%d%s' % (v, unit_to_name[unit])

    if v > 10:
        vlen = 1
    elif v > 1:
        vlen = 2
    else:
        vlen = 3

    return ('%.' + str(vlen) + 'f%s') % (v, unit_to_name[unit])


def humannum(data, unit=None, include=None, exclude=None):

    if type(data) == type({}):

        data = data.copy()

        keys = set(data.keys())
        if include is not None:
            keys = keys & set(include)

        if exclude is not None:
            keys = keys - set(exclude)

        for k in keys:
            data[k] = humannum(data[k])

        return data

    elif type(data) == type([]):
        return [humannum(x) for x in data]

    elif type(data) == type(''):
        return data

    elif type(data) in [type(0), type(0L)]:
        return humannum_int(data, unit=unit)

    elif type(data) == type(0.1):
        if data > 999:
            return humannum_int(int(data), unit=unit)
        elif abs(data) < 0.0000000001:
            return '0'
        else:
            return '%.2f' % (data)

    else:
        return data


def parseint(data):
    return int(parsenum(data))


def parsenum(data):

    if type(data) in (type(0), type(0L)):
        return data

    if type(data) not in types.StringTypes:
        return data

    if data == '':
        return 0

    data = data.upper().rstrip('B').rstrip('I')

    unit_name = data[-1]

    if unit_name in unit_to_value:
        val = float(data[:-1]) * unit_to_value[unit_name]
    else:
        val = float(data)

    if val == int(val):
        val = int(val)

    return val
