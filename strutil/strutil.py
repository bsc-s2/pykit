#!/usr/bin/env python2.6
# coding: utf-8


import types


def line_pad(linestr, padding=''):

    lines = linestr.split("\n")

    if type(padding) in types.StringTypes:
        lines = [padding + x for x in lines]

    elif callable(padding):
        lines = [padding(x) + x for x in lines]

    lines = "\n".join(lines)

    return lines


def format_line(items, sep=' ', aligns=''):

    listtype = (type([]), type(()))

    aligns = [x for x in aligns] + [''] * len(items)
    aligns = aligns[:len(items)]
    aligns = ['r' if x == 'r' else x for x in aligns]

    items = [(x if type(x) in listtype else [x])
             for x in items]

    items = [[str(y) for y in x]
             for x in items]

    maxHeight = max([len(x) for x in items])

    max_width = lambda x: max([len(y) for y in x])
    widths = [max_width(x) for x in items]

    items = [(x + [''] * maxHeight)[:maxHeight]
             for x in items]

    lines = []
    for i in range(maxHeight):
        line = []
        for j in range(len(items)):
            width = widths[j]
            elt = items[j][i]
            if aligns[j] == 'l':
                elt = elt.ljust(width)
            else:
                elt = elt.rjust(width)
            line.append(elt)
        line = sep.join(line)

        lines.append(line)

    return "\n".join(lines)
