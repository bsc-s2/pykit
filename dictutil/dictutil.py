#!/bin/env python2
# coding: utf-8

import copy
import operator
from collections import defaultdict


def depth_iter(mydict, ks=None, maxdepth=10240,
               intermediate=False, empty_leaf=False,
               is_allowed=None):

    ks = ks or []

    dickeys = sorted(mydict.keys())
    for k in dickeys:

        v = mydict[k]

        ks.append(k)

        if len(ks) >= maxdepth:
            if is_allowed is None or is_allowed(ks, v):
                yield ks, v
        else:
            if isinstance(v, dict):

                if is_allowed is not None:
                    if is_allowed(ks, v):
                        yield ks, v
                else:
                    if intermediate or (empty_leaf and len(v) == 0):
                        yield ks, v

                for _ks, v in depth_iter(v, ks,
                                         maxdepth=maxdepth,
                                         intermediate=intermediate,
                                         empty_leaf=empty_leaf,
                                         is_allowed=is_allowed,
                                         ):
                    yield _ks, v
            else:
                if is_allowed is None or is_allowed(ks, v):
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

    _keys = key_path

    if isinstance(key_path, basestring):
        _keys = key_path.split('.')

    for k in _keys:

        try:
            key = _translate_var(k, vars)
        except KeyError:
            if ignore_vars_key_error:
                return _default
            else:
                raise

        if key not in node:
            return _default

        node = node[key]

    return node


def make_getter_str(key_path, default=0):

    s = 'lambda dic, vars={}: dic'

    _keys = key_path
    if isinstance(key_path, basestring):
        _keys = key_path.split('.')

    for k in _keys:

        k_str = _translate_var_str(k)

        s += '.get(%s, {})' % (k_str, )

    s = s[:-3] + 'vars.get("_default", ' + repr(default) + '))'

    return s


def _translate_var(k, vars):
    if isinstance(k, basestring):
        if k.startswith('$'):
            k = k[1:]
            if k in vars:
                return str(vars[k])
            else:
                raise KeyError('{k} does not exist in vars: {vars}'.format(
                    k=k, vars=vars))
        else:
            return k
    elif isinstance(k, tuple):

        return tuple(_translate_var(kk, vars) for kk in k)

    else:
        return k


def _translate_var_str(k):
    if isinstance(k, basestring):
        if k.startswith('$'):
            return 'str(vars.get("%s", "_"))' % (k[1:],)
        else:
            return '"' + k + '"'

    elif isinstance(k, tuple):
        s = "("
        for kk in k:
            s += _translate_var_str(kk) + ','
        return s + ")"
    else:
        return repr(k)


def make_getter(key_path, default=0):
    return eval(make_getter_str(key_path, default=default))


def make_setter(key_path, value=None, incr=False):
    _keys = key_path
    if isinstance(key_path, basestring):
        _keys = key_path.split('.')

    def_val = value

    def _set_dict(dic, value=None, vars={}):

        k = 'self'
        _node = {'self': dic}

        for _k in _keys:

            if k not in _node:
                _node[k] = {}
            _node = _node[k]

            k = _translate_var(_k, vars)

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


def combineto(a, b, op, exclude=None, recursive=True):

    if not isinstance(b, dict):
        return a

    if exclude is None:
        exclude = {}

    for k, vb in b.iteritems():
        sub_exclude = exclude.get(k)

        if sub_exclude is True:
            continue

        if k not in a:
            # use the default constructor of `vb` to get a `zero` value.
            va = type(vb)()
        else:
            va = a[k]

        if isinstance(vb, dict):
            if recursive:
                a[k] = combineto(va, vb, op, exclude=sub_exclude, recursive=recursive)
            else:
                continue
        else:
            a[k] = op(va, vb)

    return a


def combine(a, b, op, exclude=None, recursive=True):
    r = copy.deepcopy(a)
    combineto(r, b, op, exclude=exclude, recursive=recursive)
    return r


def addto(a, b, exclude=None, recursive=True):
    op = operator.add
    return combineto(a, b, op, exclude=exclude, recursive=recursive)


def add(a, b, exclude=None, recursive=True):
    r = copy.deepcopy(a)
    addto(r, b, exclude=exclude, recursive=recursive)
    return r


def subdict(source, flds, use_default=False, default=None, deepcopy=False, deepcopy_default=False):

    result = {}

    for k in flds:

        if k in source:
            val = source[k]
            result[k] = _copy_value(val, deepcopy)
            continue

        if use_default is False:
            continue

        if callable(default):
            result[k] = default(k)
            continue

        result[k] = _copy_value(default, deepcopy_default)

    return result


def _copy_value(val, deepcopy=False):

    if deepcopy:
        return copy.deepcopy(val)

    return val
