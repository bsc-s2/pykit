<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Classes](#classes)
    - [cacheable.LRU](#cacheablelru)
    - [cacheable.Cacheable](#cacheablecacheable)
- [Methods](#methods)
    - [LRU[key]](#lrukey)
    - [cacheable.cache](#cacheablecache)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

#   Name

cacheable

#   Status

The library is considered production ready.

#   Synopsis

```python
from pykit import cacheable

# create a `LRU`, capacity:10 timeout:60
c = cacheable.LRU(10, 60)

# set value like the `dict`
c['key'] = 'val'

# get value like the `dict`
# if item timeout, delete it and raise `KeyError`
# if item not exist, raise `KeyError`
try:
    val = c['key']
except KeyError:
    print('key error')
```

```python
from pykit import cacheable

cache_data = {
    'key1': 'val_1',
    'key2': 'val_2',
}

# define the function with a decorator
@cacheable.cache('cache_name', capacity=100, timeout=60,
                    is_deepcopy=False, mutex_update=False)
def get_data(param):
    return cache_data.get(param, '')

# call `get_data`, if item has not been cached, cache the return value
data = get_data('key1')

# call `get_data` use the same param, data will be got from cache
time.sleep(30)
data = get_data('key1')

# if item timeout, when call `get_data`, cache again
time.sleep(70)
data = get_data('key1')

# define a method with a decorator
class MethodCache(object):

    @cacheable.cache('method_cache_name', capacity=100, timeout=60,
                        is_deepcopy=False, mutex_update=False)
    def get_data(self, param):
        return cache_data.get(param, '')

mm = MethodCache()
data = mm.get_data('key2')
```

#   Description

Cache data which access frequently.

#   Classes

##  cacheable.LRU

**syntax**:
`cacheable.LRU(capacity, timeout=60)`

Least Recently Used Cache.

**arguments**:

-   `capacity`: capacity of `LRU`, when the size of `LRU` is greater than `capacity` * 1.5,
    clean old items until the size is equal to `capacity`

-   `timeout`: max cache time of item, unit is second, default is 60

##  cacheable.Cacheable

**syntax**:
`cacheable.Cacheable(capacity=1024 * 4, timeout=60, is_deepcopy=True, mutex_update=False)`

Create a `LRU` object, all items will be cached in it.

**arguments**:

-   `capacity`: for create `LRU` object, default is 1024 * 4

-   `timeout`: for create `LRU` object, default is 60, unit is second

-   `is_deepcopy`: `cacheable.cache` return a decorator that use `is_deepcopy`
    to return deepcopy or reference of cached item.

    -   `True`: return deepcopy of cached item

    -   `False`: return reference of cached item

-   `mutex_update`: allows only one thread to update the cache item.
     Default is `False`.

    -   `True`: mutex update

    -   `False`: concurrently update

#   Methods

##  LRU[key]

`LRU` contain `__getitem__` and `__setitem__`,
so can get value and set value like `dict`

-   `LRU[key]`: return the item of `LRU` with `key`.

    If item exist, move it to the tail to avoid to be cleaned.

    Raise a `KeyError` if `key` is not in `LRU` or has been timeout.

    ```python
    from pykit import cacheable
    # create `LRU`, capacity:10, timeout:60
    lru = cacheable.LRU(10, 60)

    # set `lru['a']` to 'val_a'
    lru['a'] = 'val_a'

    sleep_time = 30
    try:
        time.sleep(sleep_time)
        val = lru['a']
        # if sleep_time <= timeout of LRU, return the value
        # if sleep_time > timeout of LRU, delete it and raise a `KeyError`
    except KeyError as e:
        print('key not in lru')

    try:
        val = lru['b']
        # if item not in lru, raise a `KeyError`
    except KeyError as e:
        print('key not in lru')
    ```

-   `LRU[key] = value`: set `LRU[key]` to `value` and
    move it to tail of `LRU` to avoid to be cleaned.

    If size of `LRU` is greater than `capacity` * 1.5,
    clean items from head until size is equal to `capacity`.

    ```python
    from pykit import cacheable
    # create a `LRU`, capacity:2 timeout:60
    c = cacheable.LRU(2, 60)

    # insert new item to the tail of `LRU`
    c['a'] = 'val_a'
    c['b'] = 'val_b'
    c['c'] = 'val_c'

    # after insert `d`, `a` and `b` will be cleaned
    c['d'] = 'val_d'
    ```

##  cacheable.cache

**syntax**:
`cacheable.cache(name, capacity=1024 * 4, timeout=60, is_deepcopy=True, mutex_update=False)`

If not exist, create a `cacheable.Cacheable` and save it, else use exist one.

```python
from pykit import cacheable

need_cache_data_aa = {'key': 'val_aa'}
need_cache_data_bb = {'key': 'val_bb'}

#use different `name` create two objects, they don't have any relation.
@cacheable.cache('name_aa', capacity=100, timeout=60, is_deepcopy=False, mutex_update=False)
def cache_aa(param):
    return need_cache_data_aa.get(param, '')

@cacheable.cache('name_bb', capacity=100, timeout=60, is_deepcopy=False, mutex_update=False)
def cache_bb(param):
    return need_cache_data_bb.get(param, '')
```

**arguments**:

-   `name`: for distinguishing different `cacheable.Cacheable`

-   `capacity`: used as `capacity` of `cacheable.Cacheable`

-   `timeout`: used as `timeout` of `cacheable.Cacheable`

-   `is_deepcopy`: used as `is_deepcopy` of `cacheable.Cacheable`

-   `mutex_update`: used as `mutex_update` of `cacheable.Cacheable`

**return**:
A decorator function that it checks whether the data has been cached,
if not or has been timeout, cache and return the data.

```python
from pykit import cacheable

need_cache_data = {
    'key1': 'val_1',
    'key2': 'val_2',
}

@cacheable.cache('cache', capacity=100, timeout=60, is_deepcopy=False, mutex_update=False)
def get_data(key):
    return need_cache_data.get(key, '')

# params of `get_data` are used to generate key of LRU
# if params are different, cache them as different items
get_data('key1')
get_data('key2')
```

#   Author

Baohai Liu(刘保海) <baohai.liu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Baohai Liu(刘保海) <baohai.liu@baishancloud.com>
