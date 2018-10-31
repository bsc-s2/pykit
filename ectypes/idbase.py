#!/usr/bin/env python
# coding: utf-8

from collections import namedtuple


class IDBase(str):

    _attrs = (
        # ('server_id', 0, 12, ServerID),
        # ('_non_attr', 12, 13, validator),
        # ('mountpoint_index', 13, 16, MountPointIndex),
        # ('port', 13, 16, _port),
    )

    _str_len = 0

    _tostr_fmt = ''  # '{attr_1}-{attr_2:0>3}'

    def __new__(clz, *args, **kwargs):

        if len(args) + len(kwargs) == 1:
            # New from a single serialized string
            s = (list(args) + kwargs.values())[0]
            s = str(s)
            return clz._new_by_str(s)
        else:
            # multi args: new by making an instance
            return clz._new_by_attrs(*args, **kwargs)

    @classmethod
    def _new_by_attrs(clz, *args, **kwargs):

        # Create a namedtuple to simplify arguments receiving

        tuple_type = namedtuple('_' + clz.__name__,
                                ' '.join([x[0]
                                          for x in clz._attrs
                                          if clz._is_key_attr(x)
                                          ]))

        t = tuple_type(*args, **kwargs)
        # warn: if the value is float and _tostr_fmt is with float format,
        #       raise ValueError. Not convert to string?
        s = clz._tostr_fmt.format(**{k: str(v)
                                     for k, v in t._asdict().items()})

        return clz._new_by_str(s)

    @classmethod
    def _new_by_str(clz, s):

        if len(s) != clz._str_len:
            raise ValueError('Expected {clz} length'
                             ' to be {l} but {sl}: {s}'.format(
                                 clz=clz.__name__,
                                 l=clz._str_len,
                                 sl=len(s),
                                 s=s))

        x = super(IDBase, clz).__new__(clz, s)

        id_attrs = []

        for attr_definition in clz._attrs:

            k, start_idx, end_idx, attr_type, opt = clz._normalize(attr_definition)

            if opt['self']:
                val = x
            else:
                val = attr_type(s[start_idx:end_idx])

                if opt['embed']:
                    for a in val._id_base_attrs:
                        if not a.startswith('_'):
                            super(IDBase, x).__setattr__(a, getattr(val, a))
                            id_attrs.append(a)


            if k.startswith('_'):
                continue

            super(IDBase, x).__setattr__(k, val)
            id_attrs.append(k)

        super(IDBase, x).__setattr__('_id_base_attrs', tuple(id_attrs))

        return x

    @classmethod
    def _is_key_attr(clz, attr_definition):
        name, s, e, attr_type, opt = clz._normalize(attr_definition)

        if name.startswith('_'):
            return False

        return opt['key_attr']

    @classmethod
    def _normalize(clz, attr_definition):

        name, s, e, attr_type, opt = (attr_definition + (None,))[:5]

        if opt is None:
            opt = {}
        elif opt is False:
            opt = {'key_attr': False}
        elif opt == 'self':
            opt = {'key_attr': False, 'self': True}
        elif opt == 'embed':
            opt = {'embed': True}
        else:
            pass

        tmpl = {'key_attr': True,
                'self': False,
                'embed': False,
                }

        tmpl.update(opt)
        opt = tmpl

        if opt['self']:
            opt['key_attr'] = False

        return name, s, e, attr_type, opt


    def __setattr__(self, n, v):
        raise TypeError('{clz} does not allow to change attribute'.format(
            clz=self.__class__.__name__))

    def as_tuple(self):
        lst = []
        for attr_definition in self._attrs:
            k = attr_definition[0]
            if IDBase._is_key_attr(attr_definition):
                lst.append(getattr(self, k))

        return tuple(lst)
