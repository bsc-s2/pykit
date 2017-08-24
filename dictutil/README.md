<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Methods](#methods)
  - [dictutil.attrdict](#dictutilattrdict)
  - [dictutil.attrdict_copy](#dictutilattrdict_copy)
  - [dictutil.depth_iter](#dictutildepth_iter)
  - [dictutil.breadth_iter](#dictutilbreadth_iter)
  - [dictutil.get](#dictutilget)
  - [dictutil.make_getter](#dictutilmake_getter)
  - [dictutil.make_setter](#dictutilmake_setter)
    - [Synopsis](#synopsis-1)
  - [dictutil.contains](#dictutilcontains)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

dictutil

It provides with several dict operation functions.

#   Status

This library is considered production ready.

#   Synopsis

Depth first search a dictionary

```python
from pykit import dictutil

mydict = {'a':
             {'a.a': 'v-a.a',
              'a.b': {'a.b.a': 'v-a.b.a'},
              'a.c': {'a.c.a': {'a.c.a.a': 'v-a.c.a.a'}}
             }
         }

# depth-first iterative the dict
for rst in dictutil.depth_iter(mydict):
    print rst

# output:
#     (['a', 'a.c', 'a.c.a', 'a.c.a.a'], 'v-a.c.a.a')
#     (['a', 'a.b', 'a.b.a'], 'v-a.b.a')
#     (['a', 'a.a'], 'v-a.a')
```

Breadth first search a dictionary

```python
for rst in dictutil.breadth_iter(mydict):
    print rst

# output:
#     (['a'],                            {'a.c': {'a.c.a': {'a.c.a.a': 'v-a.c.a.a'}}, 'a.b': {'a.b.a': 'v-a.b.a'}, 'a.a': 'v-a.a'})
#     (['a', 'a.a'],                     'v-a.a')
#     (['a', 'a.b'],                     {'a.b.a': 'v-a.b.a'})
#     (['a', 'a.b', 'a.b.a'],            'v-a.b.a')
#     (['a', 'a.c'],                     {'a.c.a': {'a.c.a.a': 'v-a.c.a.a'}})
#     (['a', 'a.c', 'a.c.a'],            {'a.c.a.a': 'v-a.c.a.a'})
#     (['a', 'a.c', 'a.c.a', 'a.c.a.a'], 'v-a.c.a.a')

#
```

Make a predefined dictionary item getter.

```python
import dictutil

records = [
    {"event": 'log in',
     "time": {"hour": 10, "minute": 30, }, },

    {"event": 'post a blog',
     "time": {"hour": 10, "minute": 40, }, },

    {"time": {"hour": 11, "minute": 20, }, },

    {"event": 'log out',
     "time": {"hour": 11, "minute": 20, }, },
]

get_event = dictutil.make_getter('event', default="NOTHING DONE")
get_time = dictutil.make_getter('time.$field')

for record in records:

    ev = get_event(record)

    tm = "%d:%d" % (get_time(record, {"field": "hour"}),
                    get_time(record, {"field": "minute"}))

    print "{ev:<12}   at {tm}".format(ev=ev, tm=tm)

# output:
# log in         at 10:30
# post a blog    at 10:40
# NOTHING DONE   at 11:20
# log out        at 11:20
```

#   Methods

## dictutil.attrdict

**syntax**:
`dictutil.attrdict()`

**syntax**:
`dictutil.attrdict(mapping, **kwargs)`:<br/>
new dictionary initialized from a mapping object's (key, value) pairs, with additional name=value pairs.

**syntax**:
`dictutil.attrdict(iterable, **kwargs)`:<br/>
new dictionary initialized as if via: `d = {}; for k, v in iterable: d[k] = v`

Make a dict-like object whose keys can also be accessed with attribute.

Argument is exactly the same as `dict()`.

```
a = dictutil.attrdict(x=3, y={'z':4})
a['x']  # 3
a.x     # 3
a.y     # {'z':4}
a.y.z   # 4
```

This funciton also works well with circular references.

```
x = {}
x['x'] = x
ad = dictutil.attrdict(x)

print(ad.x is ad) # True: circular references are kept
```

Pros:

- It actually works!
- No dictionary class methods are shadowed (e.g. .keys() work just fine)
- Attributes and items are always in sync
- Trying to access non-existent key as an attribute correctly raises AttributeError instead of KeyError

Cons:

- Methods like .keys() will not work just fine if they get overwritten by incoming data
- Causes a memory leak in `Python < 2.7.4 / Python3 < 3.2.3`
- Pylint goes bananas with E1123(unexpected-keyword-arg) and E1103(maybe-no-member)
- For the uninitiated it seems like pure magic.

Issues:

- Dictionary key overrides dictionary methods:

  ```
  d = AttrDict()
  d.update({'items':["a", "b"]})
  d.items() # TypeError: 'list' object is not callable
  ```

**arguments**:
are same as `dict()`, a dictionary or kwargs are both acceptable.

**return**:
an object provides with dictionary item access with attribute.


##  dictutil.attrdict_copy

Same as `dictutil.attrdict`, except that:

-   every time to access it by an attribute or by a key,
    the value is copied before returning.

-   It does not allow to set its attribute or key, such as `a["x"]=1` or `a.x=1`.


## dictutil.depth_iter

**syntax**:
`dictutil.depth_iter(mydict, ks=None, maxdepth=10240, intermediate=False)`

**arguments**:

-   `mydict`:
    the dict that you want to iterate on.

-   `ks`:
    the argument could be a `list`,  it would be seted ahead of key's list in
    results of iteration

    ```python
    for rst in dictutil.depth_iter(mydict, ks=['mykey1','mykey2']):
        print rst

    # output:
    #     (['mykey1', 'mykey2', 'k1', 'k13', 'k131', 'k1311'], 'v-a.c.a.a')
    #     (['mykey1', 'mykey2', 'k1', 'k12', 'k121'], 'v-a.b.a')
    #     (['mykey1', 'mykey2', 'k1', 'k11'], 'v-a.a')

    ```

-   `maxdepth`:
    specifies the max depth of iteration.

    ```python
    for rst in dictutil.depth_iter(mydict, maxdepth=2):
        print rst

    # output
    #     (['k1', 'k13'], {'k131': {'k1311': 'v-a.c.a.a'}})
    #     (['k1', 'k12'], {'k121': 'v-a.b.a'})
    #     (['k1', 'k11'], 'v-a.a')
    ```

-   `intermediate`:
    if it is `True`, the method will show the intermediate key path those
    points to a non-leaf descendent.
    By default it is `False`.

    ```python
    mydict = {'a':
                 {'a.a': 'v-a.a',
                  'a.b': {'a.b.a': 'v-a.b.a'},
                  'a.c': {'a.c.a': {'a.c.a.a': 'v-a.c.a.a'}}
                 }
             }
    for keys, vals in dictutil.depth_iter(mydict, intermediate=True):
       print keys

    # output:
    #     ['a']                              # intermediate
    #     ['a', 'a.a']
    #     ['a', 'a.b']                       # intermediate
    #     ['a', 'a.b', 'a.b.a']
    #     ['a', 'a.c']                       # intermediate
    #     ['a', 'a.c', 'a.c.a']              # intermediate
    #     ['a', 'a.c', 'a.c.a', 'a.c.a.a']

    ```

**return**:
an iterator. Each element it yields is a tuple of keys and value.

## dictutil.breadth_iter

**syntax**:
`dictutil.breadth_iter(mydict)`

**arguments**:

-   `mydict`:
    the dict you want to iterative

**return**:
an iterator, each element it yields is a tuple that contains keys and value.

##  dictutil.get

Returns the value of the item specified by `key_path`.

`dictutil.get(dic, key_path, vars=v, default=3)`
 is equivalent to
`dictutil.make_getter(key_path, default=3)(dic, vars=v)`

**syntax**:
`dictutil.get(dic, key_path, vars=None, default=0, ignore_vars_key_error=None)`

**arguments**:

-   `dic`:
    dictionary.

-   `key_path`:
    is a dot separated path string of key hierarchy to get an item from a
    dictionary.

    Example: `foo.bar` is same as `some_dict["foo"]["bar"]`.

-   `vars`:
    is a dictionary contains dynamic keys in `key_path`.

    `dictutil.get({'a':1}, '$foo', vars={"foo":"a"})`
    is same as
    `dictutil.get({'a':1}, 'a')`

-   `default`:
    is the default value if the item is not found.
    For example when `foo.bar` is used on a dictionary `{"foo":{}}`.

    It must be a primitive value such as `int`, `float`, `bool`, `string` or `None`.

-   `ignore_vars_key_error`:
    specifies if it should ignore when a dynamic key does not present in
    `vars`.

    By default it is `True`.

    If it is `True`, default value is returned.

    If it is `False`, `KeyError` will be raised.

**return**:
item value it found by `key_path`, or `default`

##  dictutil.make_getter

**syntax**:
`dictutil.make_getter(key_path, default=0)`

It creates a lambda that returns the value of the item specified by
`key_path`.

```python
get_hour = dictutil.make_getter('time.hour')
print get_hour({"time": {"hour": 11, "minute": 20}})
# 11

get_minute = dictutil.make_getter('time.minute')
print get_minute({"time": {"hour": 11, "minute": 20}})
# 20

get_second = dictutil.make_getter('time.second', default=0)
print get_second({"time": {"hour": 11, "minute": 20}})
# 0
```


**arguments**:

-   `key_path`:
    is a dot separated path string of key hierarchy to get an item from a
    dictionary.

    Example: `foo.bar` is same as `some_dict["foo"]["bar"]`.

-   `default`:
    is the default value if the item is not found.
    For example when `foo.bar` is used on a dictionary `{"foo":{}}`.

    It must be a primitive value such as `int`, `float`, `bool`, `string` or `None`.

**return**:
the item value found by key_path, or the default value if not found.

##  dictutil.make_setter

**syntax**:
`dictutil.make_setter(key_path, default=None, incr=False)`

It creates a function `setter(dic, value=None, vars={})` that can be used to
set(or increment) the item value specified by `key_path` in a dictionary `dic`.

### Synopsis

```python
tm = {"time": {"hour": 0, "minute": 0}}

set_hour = dictutil.make_setter('time.hour')
set_hour(tm, 12)
print tm
# {"time": {"hour": 12, "minute": 0}}

incr_minute = dictutil.make_setter('time.minute', incr=True)
incr_minute(tm, 1)
print tm
# {"time": {"hour": 12, "minute": 1}}

incr_minute(tm, 2)
print tm
# {"time": {"hour": 12, "minute": 3}}
```

**arguments**:

-   `key_path`:
    is a dot separated key path to locate an item in a dictionary.

    Example: `foo.bar` is same as `some_dict["foo"]["bar"]`.

-   `value`:
    is the value to use if `setter` is called with its own `value` set to `None`.

    `value` can be a `callable`, such as `function` or `lambda`.
    If it is a `callable`, it must be able to accept one argument `vars`.

    `vars` is passed to the `setter` by the caller.

    ```python
    set_minute = dictutil.make_setter('time.minute', value=lambda vars: int(time.time()) % 3600 / 60)
    tm = {"time": {"hour": 11, "minute": 20}}
    print set_minute(tm)
    # current time minute
    ```

-   `incr`:
    specifies whether the value should be overwritten(`incr=False`) or
    added to present value(`incr=True`).

    If `incr=True`, `value` must supports plus operation: `+`, such as a `int`,
    `float`, `string`, `tuple` or `list`.

**return**:
a function `setter(dic, value=None, vars={})` that can be used to set an item
value in a dictionary to `value`(or to the `value` that is passed to
`make_setter`, if the `value` passed to setter is `None`).

`vars` is a dictionary that contains dynamic item keys.

`setter` returns the result value.

```python
_set = dictutil.make_setter('time.$subfield')
tm = {"time": {"hour": 0, "minute": 0}}

# set minute:
print _set(tm, 22, vars={'subfield': 'minute'})
# {"time": {"hour": 0, "minute": 22}}

# set hour:
print _set(tm, 15, vars={'subfield': 'hour'})
# {"time": {"hour": 15, "minute": 0}}
```

## dictutil.contains

**syntax**:
`dictutil.contains(a, b)`

**arguments**:

-   `a`:
    is a containing dict or primitive type value.

-   `b`:
    is a contained dict or primitive type value.

**return**:
`true` if `a` contains `b`. Or `false`

heck if dict `a` contains dict `b`.

**Contain** means `key_path` for `b` is a subset of `key_path` for `a`.

To explain this concept, we need two definitions:

-   `key_path`: is a series of dict keys to access (nested) dict field.
    For example, there is a dict `a = {"x":{"y":3}}`, key path `.x.y` is used to
    access `3`.

    A **non-leaf** `key_path` is a prefix of some other `key_path` and is used
    to access an intermedia dict, such as `.x`.

    A **leaf** `key_path` is **NOT** a prefix of any other `key_path` and is
    used to access a primitive value, such as `.x.y`.

-   `contain`:
    There are two dict `a` and `b`.
    For any finite `key_path` `pb` in `b`, if:

    -   `pb` is also a valid `key_path` in `a`,
    -   and: if `pb` is a leaf `key_path` and the values referred by `pb` in `a`
        and `b` are the same.

    then `a` contains `b`.

    Example:

    ```
    a = {"x":1}
    b = {"x":1, "y":2}
    ```

    In the above example the only `key_path` in `a` is `.x` which is also a valid `key_path`
    in `b` and `a.x == b.x`. Thus `b contains a`.

    But `a does NOT contain b` because `.y` in `b` is not a valid `key_path` in
    `a`.

    ```
    a = {"x":{}}
    b = {"x":1, "y":2}
    ```

    In the above example `b does NOT contains a` because `a.x` is a dict but
    `b.x` is a number.

    ```
    a = {"x":{}}
    b = {"x":{"x":{}}}
    a.x.x = a
    b.x.x.x = b
    ```

    In the above example `b contains a` and `a contains b` because they both
    have the same key path set: `(.x)+`:

    ```
    .x
    .x.x
    .x.x.x
    ...
    ```

    If a and b are both primitive type, "contains" is defined by a==b.

---

The algorithm to compare two dict recursively:

For dicts with circular references, such as:

```
a.x.x = a
b.x.x.x = b

and

a.x.x = b
b.x.x.x = a
```

We compare two dicts by comparing every `key_path` in them.
In the above two examples, `a` and `b` contain each other, because the
set of `key_path` in `a` and `b` are both: `(.x)+`.

Algorithm:

-   Depth first traverse `b` to iterate all possible leaf and non-leaf `key_path` in it.

-   And check if this `key_path` is also valid in `a`.

-   If a `key_path` is a leaf `key_path`, the values this `key_path` referring
    in `a` and `b` must be the same.

-   If a `key_path` is a non-leaf `key_path`, and they points to a pair of nodes
    we have already compared, stop traversal of this `key_path`, because further
    traversal does not produce more possible `key_path`.

    Thus we record every pair of `a` tree node and `b` tree node that we have
    compared in the traversal.

#   Author

break wang (王显宝) <breakwang@outlook.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 break wang (王显宝) <breakwang@outlook.com>
