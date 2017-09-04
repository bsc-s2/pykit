#!/bin/env python2
# coding: utf-8

import copy
from collections import defaultdict


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


def get(dic, key_path, vars=None, default=0, ignore_vars_key_error=None):

    if vars is None:
        vars = {}

    if ignore_vars_key_error is None:
        ignore_vars_key_error = True

    _default = vars.get('_default', default)
    node = dic

    _keys = key_path.split('.')
    if _keys == ['']:
        return node

    for k in _keys:

        if k.startswith('$'):
            k = k[1:]
            if k in vars:
                key = vars[k]
            else:
                if ignore_vars_key_error:
                    return _default
                else:
                    raise KeyError('{k} does not exist in vars: {vars}'.format(
                        k=k, vars=vars))
        else:
            key = k

        if key not in node:
            return _default

        node = node[key]

    return node


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
            # use the default constructor to get a default "zero" value
            _node[k] = type(val_to_set)()

        if incr:
            _node[k] += val_to_set
        else:
            _node[k] = val_to_set

        return _node[k]

    return _set_dict


def _contains(a, b, ref_table):
    if a is b:
        return True

    if (isinstance(a, list) and isinstance(b, list)
            or (isinstance(a, tuple) and isinstance(b, tuple))):

        if len(a) < len(b):
            return False

        for i, v in enumerate(b):
            if not _contains(a[i], v, ref_table):
                return False
        else:
            return True

    if not isinstance(a, dict) or not isinstance(b, dict):
        return a == b

    id_a, id_b = id(a), id(b)

    if ref_table[id_a].get(id_b) is not None:
        return ref_table[id_a][id_b]

    ref_table[id_a][id_b] = True

    for k, v in b.items():
        if a.get(k) is None:
            return False

        if not _contains(a[k], v, ref_table):
            return False

    return True


def contains(a, b):
    return _contains(a, b, defaultdict(dict))


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


class AttrDictCopy(dict):

    # Allow to set attribute or key.
    # But when get attribute or key, the value is copied before returning.
    # To prevent changing original data.

    def __getattr__(self, k):

        if k not in self:
            raise AttributeError(repr(k) + ' not found')

        return self[k]

    def __setattr__(self, k, v):
        raise AttributeError('AttrDictCopy does not allow to set attribute')

    def __getitem__(self, k):

        if k not in self:
            raise KeyError(repr(k) + ' not found')

        v = super(AttrDictCopy, self).__getitem__(k)
        if isinstance(v, AttrDictCopy):
            # reduce it to a normal dict, or deepcopy can not set items to the new instance
            v = v.as_dict()
            v = copy.deepcopy(v)
            return _attrdict(AttrDictCopy, v, {})
        else:
            return copy.deepcopy(v)

    def __setitem__(self, k, v):
        raise KeyError('AttrDictCopy does not allow to set key')

    def as_dict(self):
        d = {}

        for k in self.keys():
            v = super(AttrDictCopy, self).__getitem__(k)
            if isinstance(v, AttrDictCopy):
                v = v.as_dict()

            d[k] = v

        return d


def attrdict(*args, **kwargs):
    """
    Make a dict-like object whose keys can also be accessed with attribute.
    You can use an AttrDict instance just like using a dict instance.
    """

    d = dict(*args, **kwargs)
    return _attrdict(AttrDict, d, {})


def attrdict_copy(*args, **kwargs):

    d = dict(*args, **kwargs)
    return _attrdict(AttrDictCopy, d, {})


def _attrdict(attrdict_clz, d, ref):

    if not isinstance(d, dict):
        return d

    if isinstance(d, attrdict_clz):
        return d

    if id(d) in ref:
        return ref[id(d)]

    # id() is the memory address of an object, thus it is unique.
    ad = attrdict_clz(d)
    ref[id(d)] = ad

    for k in d.keys():
        sub_ad = _attrdict(attrdict_clz, d[k], ref)
        super(attrdict_clz, ad).__setitem__(k, sub_ad)

    return ad
