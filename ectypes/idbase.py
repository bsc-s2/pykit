#!/usr/bin/env python
# coding: utf-8

from collections import namedtuple


class IDBase(str):

    _attrs = (
        # ('server_id', 0, 12, ServerID),
        # ('_non_attr', 12, 13, validator),
        # ('mountpoint_index', 13, 16, MountPointIndex),
    )

    _str_len = 0

    _tostr_fmt = '' # '{attr_1}-{attr_2:0>3}'

    def __new__(clz, *args, **kwargs):

        if len(args) + len(kwargs) == 1:
            # New from a single serialized string
            s = (list(args) + kwargs.values())[0]
            s = str(s)

            if len(s) != clz._str_len:
                raise ValueError('Expected {clz} length'
                                 ' to be {l} but {sl}: {s}'.format(
                                     clz=clz.__name__,
                                     l=clz._str_len,
                                     sl=len(s),
                                     s=s))

            x = super(IDBase, clz).__new__(clz, s)

            for k, start_idx, end_idx, attr_type in clz._attrs:

                val = attr_type(s[start_idx:end_idx])

                if k.startswith('_'):
                    continue

                super(IDBase, x).__setattr__(k, val)

            return x
        else:
            # multi args: new by making an instance
            return clz._make(*args, **kwargs)

    @classmethod
    def _make(clz, *args, **kwargs):

        # Create a namedtuple to simplify arguments receiving

        tuple_type = namedtuple('_' + clz.__name__,
                                ' '.join([x[0]
                                          for x in clz._attrs
                                          if not x[0].startswith('_')
                                          ]))

        t = tuple_type(*args, **kwargs)
        # warn: if the value is float and _tostr_fmt is with float format,
        #       raise ValueError. Not convert to string?
        s = clz._tostr_fmt.format(**{k: str(v)
                                     for k, v in t._asdict().items()})

        return clz(s)

    def __setattr__(self, n, v):
        raise TypeError('{clz} does not allow to change attribute'.format(
                clz=self.__class__.__name__))

    def as_tuple(self):
        lst = []
        for k, _, _, _ in self._attrs:
            if not k.startswith('_'):
                lst.append(getattr(self, k))

        return tuple(lst)
