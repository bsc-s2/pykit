#!/bin/env python2
# coding: utf-8

import types


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


def make_getter_str(key_path, default=0):

    s = 'lambda dic, vars={}: dic'

    _keys = key_path.split('.')
    if _keys == ['']:
        return s

    for k in _keys:

        if k.startswith('$'):

            dynamic_key = 'str(vars.get("%s", "_"))' % (k[1:], )

            s += '.get(%s, {})' % (dynamic_key, )

        else:
            s += '.get("%s", {})' % (k, )

    s = s[:-3] + 'vars.get("_default", ' + repr(default) + '))'

    return s


def make_getter(key_path, default=0):
    return eval(make_getter_str(key_path, default=default))


def make_setter(key_path, value=None, incr=False):

    if key_path == '':
        raise KeyError('key_path can not be ""')

    _keys = key_path.split('.')

    def_val = value

    def _set_dict(dic, value=None, vars={}):

        k = 'self'
        _node = {'self': dic}

        for _k in _keys:

            if k not in _node:
                _node[k] = {}
            _node = _node[k]

            if _k.startswith('$'):
                k = vars.get(_k[1:])
                if k is None:
                    raise KeyError('var {_k} does not exist in vars. key_path={key_path}'.format(
                        _k=_k, key_path=key_path))

                k = str(k)

            else:
                k = _k

        if value is not None:
            val_to_set = value
        else:
            val_to_set = def_val

        if callable(val_to_set):
            val_to_set = val_to_set(vars)

        if k not in _node:
            _node[k] = _get_zero_value_of(val_to_set)

        if incr:
            _node[k] += val_to_set
        else:
            _node[k] = val_to_set

        return _node[k]

    return _set_dict


class AttrDict(dict):

    '''
    a = AttrDict({1:2}) # {1:2}
    a = AttrDict(x=3)   # {"x":3}
    a.x                 # 3
    a['x']              # 3

    Some pros:

    - It actually works!
    - No dictionary class methods are shadowed (e.g. .keys() work just fine)
    - Attributes and items are always in sync
    - Trying to access non-existent key as an attribute correctly raises AttributeError instead of KeyError

    Cons:

    - Methods like .keys() will not work just fine if they get overwritten by incoming data
    - Causes a memory leak in Python < 2.7.4 / Python3 < 3.2.3
    - Pylint goes bananas with E1123(unexpected-keyword-arg) and E1103(maybe-no-member)
    - For the uninitiated it seems like pure magic.

    Issues:

    - Dictionary key overrides dictionary methods:

      d = AttrDict()
      d.update({'items':["a", "b"]})
      d.items() # TypeError: 'list' object is not callable

    '''

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def attrdict(*args, **kwargs):
    """
    Make a dict-like object whose keys can also be accessed with attribute.
    You can use an AttrDict instance just like using a dict instance.
    """

    d = dict(*args, **kwargs)
    ref = {}

    return _attrdict(d, ref)


def _attrdict(d, ref):

    if not isinstance(d, dict):
        return d

    if isinstance(d, AttrDict):
        return d

    if id(d) in ref:
        return ref[id(d)]

    # id() is the memory address of an object, thus it is unique.
    ad = AttrDict(d)
    ref[id(d)] = ad

    for k in d.keys():
        ad[k] = _attrdict(d[k], ref)

    return ad


def _get_zero_value_of(val):

    if type(val) in types.StringTypes:
        zero_val = ''
    elif type(val) in (types.IntType, types.LongType):
        zero_val = 0
    elif type(val) is types.FloatType:
        zero_val = 0.0
    elif type(val) is types.BooleanType:
        zero_val = False
    elif type(val) is types.TupleType:
        zero_val = ()
    elif type(val) is types.ListType:
        zero_val = []
    else:
        raise ValueError('invalid type: {v}'.format(v=repr(val)))

    return zero_val
