#!/usr/bin/env python2
# coding: utf-8


import sys
import types

listtype = (types.TupleType, types.ListType)


def tokenize(line):
    # double quoted segment is preseverd

    rst = []
    n = len(line)
    i = 0

    while i < n:

        while i < n and line[i] == ' ':
            rst.append('')
            i += 1
        if i == n:
            break

        j = i

        if line[j] == '"':
            i += 1
            while i < n and line[i] != '"':
                i += 1
            if i == n:
                break

        i += 1
        while i < n and line[i] != ' ':
            i += 1

        rst.append(line[j:i])

        i += 1

    if n == 0 or line[n-1] == ' ':
        rst.append('')

    return rst


def line_pad(linestr, padding=''):

    lines = linestr.split("\n")

    if type(padding) in types.StringTypes:
        lines = [padding + x for x in lines]

    elif callable(padding):
        lines = [padding(x) + x for x in lines]

    lines = "\n".join(lines)

    return lines


def format_line(items, sep=' ', aligns=''):
    '''
    format a line with multi-row columns.

        items = [ 'name:',
                  [ 'John',
                    'j is my nick'
                  ],
                  [ 'age:' ],
                  [ 26, ],
                  [ 'experience:' ],
                  [ '2000 THU',
                    '2006 sina',
                    '2010 other'
                  ],
        ]

        format_line(items, sep=' | ', aligns = 'llllll')

    outputs:

        name: | John         | age: | 26 | experience: | 2000 THU
              | j is my nick |      |    |             | 2006 sina
              |              |      |    |             | 2010 other

    '''

    aligns = [x for x in aligns] + [''] * len(items)
    aligns = aligns[:len(items)]
    aligns = ['r' if x == 'r' else x for x in aligns]

    items = [(x if type(x) in listtype else [x])
             for x in items]

    items = [[_to_str(y)
              for y in x]
             for x in items]

    maxHeight = max([len(x) for x in items] + [0])

    max_width = lambda x: max([y.__len__()
                               for y in x] + [0])

    widths = [max_width(x) for x in items]

    items = [(x + [''] * maxHeight)[:maxHeight]
             for x in items]

    lines = []
    for i in range(maxHeight):
        line = []
        for j in range(len(items)):
            width = widths[j]
            elt = items[j][i]

            actualWidth = elt.__len__()
            elt = utf8str(elt)

            if actualWidth < width:
                padding = ' ' * (width - actualWidth)
                if aligns[j] == 'l':
                    elt = elt + padding
                else:
                    elt = padding + elt

            line.append(elt)

        line = sep.join(line)

        lines.append(line)

    return "\n".join(lines)


def struct_repr(data, key=None):
    '''
    Render a data to a multi-line structural(yaml-like) representation.

        a = {
                1: 3,
                'x': {1:4, 2:5},
                'l': [1, 2, 3],
        }
        for l in struct_repr(a):
            print l

    Output:

        1 : 3
        l : - 1
            - 2
            - 3
        x : 1 : 4
            2 : 5
    '''

    if type(data) in listtype:

        if len(data) == 0:
            return ['[]']

        max_width = 0
        elt_lines = []
        for elt in data:
            sublines = struct_repr(elt)
            sublines_max_width = max([len(x) for x in sublines])

            if max_width < sublines_max_width:
                max_width = sublines_max_width

            elt_lines.append(sublines)

        lines = []
        for sublines in elt_lines:

            # - subline[0]
            #   subline[1]
            #   ...

            lines.append('- ' + sublines[0].ljust(max_width))

            for l in sublines[1:]:
                lines.append('  ' + l.ljust(max_width))

        return lines

    elif type(data) == types.DictType:

        if len(data) == 0:
            return ['{}']

        max_k_width = 0
        max_v_width = 0

        kvs = []

        for k, v in data.items():
            k = utf8str(k)
            sublines = struct_repr(v)
            sublines_max_width = max([len(x) for x in sublines])

            if max_k_width < len(k):
                max_k_width = len(k)

            if max_v_width < sublines_max_width:
                max_v_width = sublines_max_width

            kvs.append((k, sublines))

        kvs.sort(key=key)

        lines = []
        for k, sublines in kvs:

            # foo : sub-0
            #       sub-1
            #   b : sub-0
            #       sub-0

            lines.append(k.rjust(max_k_width) + ' : ' +
                         sublines[0].ljust(max_v_width))

            for l in sublines[1:]:
                lines.append(' '.rjust(max_k_width) +
                             '   ' + l.ljust(max_v_width))

        return lines

    else:
        return [utf8str(data)]


def _get_key_and_headers(keys, rows):

    if keys is None:

        if len(rows) == 0:
            keys = []
        else:
            r0 = rows[0]

            if type(r0) == types.DictType:
                keys = r0.keys()
                keys.sort()
            elif type(r0) in listtype:
                keys = [i for i in range(len(r0))]
            else:
                keys = ['']

    _keys = []
    column_headers = []

    for k in keys:

        if type(k) not in listtype:
            k = [k, k]

        _keys.append(k[0])
        column_headers.append(str(k[1]))

    return _keys, column_headers


def _get_colors(colors, col_n):

    if colors is None:
        colors = []

    colors = colors or ([None] * col_n)

    while len(colors) < col_n:
        colors.extend(colors)

    colors = colors[:col_n]

    return colors


def format_table(rows,
                 keys=None,
                 colors=None,
                 sep=' | ',
                 row_sep=None):

    keys, column_headers = _get_key_and_headers(keys, rows)
    colors = _get_colors(colors, len(keys))

    # element of lns is a mulit-column line
    # lns = [
    #         # line 1
    #         [
    #                 # column 1 of line 1
    #                 ['name:', # row 1 of column 1 of line 1
    #                  'foo',   # row 2 of column 1 of line 1
    #                 ],
    #
    #                 # column 2 of line 1
    #                 ['school:',
    #                  'foo',
    #                  'bar',
    #                 ],
    #         ],
    # ]

    # headers
    lns = [
        [[a + ': ']
         for a in column_headers]
    ]

    for row in rows:

        if row_sep is not None:
            lns.append([[None] for k in keys])

        if type(row) == types.DictType:

            ln = [struct_repr(row.get(k, ''))
                  for k in keys]

        elif type(row) in listtype:

            ln = [struct_repr(row[int(k)])
                  if len(row) > int(k) else ''
                  for k in keys]

        else:
            ln = [struct_repr(row)]

        lns.append(ln)

    get_max_width = lambda cols: max([len(utf8str(c[0]))
                                      for c in cols] + [0])

    max_widths = [get_max_width(cols) for cols in zip(*lns)]

    rows = []
    for row in lns:

        ln = []

        for i in range(len(max_widths)):
            color = colors[i]
            w = max_widths[i]

            ln.append([ColoredString(x.ljust(w), color)
                       if x is not None else row_sep * w
                       for x in row[i]])

        rows.append(format_line(ln, sep=sep))

    return rows


def _to_str(y):
    if isinstance(y, ColoredString):
        pass
    elif type(y) in (type(0), type(0L)):
        y = str(y)
    elif type(y) in (type([]), type(()), type({})):
        y = str(y)

    return y


def utf8str(s):

    if type(s) == type(u''):
        return s.encode('utf8')
    else:
        return str(s)


def colorize(percent, total=100, ptn='{0}'):
    if total > 0:
        color = fading_color(percent, total)
    else:
        color = fading_color(-total - percent, -total)
    return ColoredString(ptn.format(percent), color)


class ColoredString(object):

    def __init__(self, v, color=None, prompt=True):
        if type(color) in types.StringTypes:
            color = _named_colors[color]

        if isinstance(v, ColoredString):
            vs = ''.join([x[0] for x in v.elts])
            self.elts = [(vs, color)]
        else:
            self.elts = [(str(v), color)]

        self._prompt = prompt

    def __str__(self):
        rst = []
        for e in self.elts:
            if e[1] is None:
                val = e[0]
            else:
                _clr = '\033[38;5;' + str(e[1]) + 'm'
                _rst = '\033[0m'

                if self._prompt:
                    _clr = '\001' + _clr + '\002'
                    _rst = '\001' + _rst + '\002'

                val = _clr + str(e[0]) + _rst

            rst.append(val)

        return ''.join(rst)

    def __len__(self):
        return sum([len(x[0])
                    for x in self.elts])

    def __add__(self, other):
        prompt = self._prompt
        if isinstance(other, ColoredString):
            prompt = prompt or other._prompt

        c = ColoredString('', prompt=prompt)
        if isinstance(other, ColoredString):
            c.elts = self.elts + other.elts
        else:
            c.elts = self.elts[:] + [(str(other), None)]
        return c

    def __mul__(self, num):
        c = ColoredString('', prompt=self._prompt)
        c.elts = self.elts * num
        return c


def fading_color(v, total):
    return _clrs[_fading_idx(v, total)]


def _fading_idx(v, total=100):
    l = len(_clrs)
    pos = int(v * l / (total + 0.0001) + 0.5)
    pos = min(pos, l - 1)
    pos = max(pos, 0)
    return pos


_clrs = [63, 67, 37, 36, 41, 46, 82, 118,
         154, 190, 226, 220, 214, 208, 202, 196]

_named_colors = {
    # by emergence levels
    'danger': _clrs[_fading_idx(100)],
    'warn': 3,
    'loaded': _clrs[_fading_idx(30)],
    'normal': 7,
    'optimal': _clrs[_fading_idx(0)],

    'dark': _clrs[1],

    # for human
    'blue': 67,
    'cyan': 37,
    'green': 46,
    'yellow': 226,
    'red': 196,
    'purple': 128,
    'white': 255,
}

def _make_colored_function(name):
    def _colored(v):
        return ColoredString(v, name)

    _colored.__name__ = name

    return _colored

for _func_name in _named_colors:
    setattr(sys.modules[__name__],
            _func_name, _make_colored_function(_func_name))
