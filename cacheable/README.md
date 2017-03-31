<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Classes](#classes)
  - [cacheable.LRU](#cacheablelru)
- [Methods](#methods)
  - [LRU.__getitem__](#lrugetitem)
  - [LRU.__setitem__](#lrusetitem)
  - [cacheable.ProcessWiseCache.cache](#cacheableprocesswisecachecache)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

# Name

cacheable

# Status

The library is considered production ready.

# Synopsis

LRU:

```

from pykit import cacheable

c = cacheable.LRU(10, 60)
c['key'] = 'val'

# exist time more than half of the timeout, old=`True`
# if timeout, delete it and raise `KeyError`
# if not exist, raise `KeyError`
try:
    (val, old) = c['key']
except KeyError:
    print('key error')

```
ProcessWiseCache:

```

from pykit import cacheable

cache_data = {'key': [1, 2]}

def get_cache_data(param):
    return cache_data.get(param, [])

# define the function with a decorator
@cacheable.ProcessWiseCache.cache('cache_name', capacity=100, timeout=60, deref=False)
def get_data(param):
    return get_cache_data(param)

# call `get_data`, if `LRU` don't contain the key, cache the return value
data = get_data('key')

# call `get_data` use the same param, data will be got from cache
time.sleep(30)
data = get_data('key')

# if item timeout in `LRU`, when call `get_data`, cache again
time.sleep(70)
data = get_data('key')

# define a function in a class with a decorator
class ClassMember(object):

    @cacheable.ProcessWiseCache.cache('cache_name_in_class', capacity=10240, timeout=5 * 60, deref=True)
    def get_data(self, param):
        return get_cache_data(param)

tt = ClassMember()
data = tt.get_data('key')

```

# Description

Cache data which access frequently.

# Classes

## cacheable.LRU

 syntax: `cacheable.LRU(capacity, timeout=60)`

 Least Recently Used Cache.

 arguments:

-   `capacity`: capacity of `LRU`, when the size of `LRU` is greater than `capacity` * 1.5, clean old items until the size is equal to `capacity`

-   `timeout`: max cache time of item, unit is second, default is 60

# Methods

## LRU.__getitem__

syntax: `LRU.__getitem__(key)`

Get cache data from `LRU`.

If exist, move it to the tail of `LRU` to avoid to be cleaned, then return the value and item old status.

If timeout, delete it and raise `KeyError`.

If not exist, raise `KeyError`.

arguments:

- `key`: key of the cache item

return: two values

- first is the cache value
- second is item old status, if cache time of item more than half of `timeout`, it is `True`, otherwise it is `False`

```
 c = cacheable.LRU(10, 10)
 c['a'] = 'val_a'

 # old is `False`
 try:
    (val, old) = c['a']
 except:
    print('key error')

 # after half of `timeout` old is `True`
 time.sleep(6)
 try:
 	(val, old) = c['a']
 except:
    print('key error')

 # if timeout, raise `KeyError`
 time.sleep(5)
 try:
 	(val, old) = c['a']
 except KeyError:
    print('key error')

# if not exist, raise `KeyError`
 try:
 	(val, old) = c['b']
 except KeyError:
    print('key error')

```

## LRU.__setitem__
syntax: `LRU.__setitem__(key, val)`

Insert cache data into the tail of `LRU` to avoid to be cleaned, if already cached, replace old item and move to the tail of `LRU`

After insert, if size of `LRU` is greater than `capacity` * 1.5, clean old items until size is equal to `capacity`

 ```
 c = cacheable.LRU(2, 60)

 # insert new item to the tail of `LRU`
 c['a'] = 'val_a'
 c['b'] = 'val_b'
 c['c'] = 'val_c'

 # after insert `d`, `a` and `b` will be cleaned
 c['d'] = 'val_d'

 ```

arguments:

 - `key`: for distinguishing items of `LRU`

 - `val`: need cached value

return: nothing

## cacheable.ProcessWiseCache.cache

 syntax:`cacheable.ProcessWiseCache.cache(name, capacity=1024 * 4, timeout=60, deref=True, key_extractor=None)`

 This is a `classmethod`, for init a `cacheable.ProcessWiseCache` object, it use `LRU` cache data.

```

need_cache_data_aa = {'key': [0]}
need_cache_data_bb = {'key': [1]}

#init two objects, they don't have any relation.
@cacheable.ProcessWiseCache.cache('name_aa', capacity=100, timeout=60, deref=False)
def cache_aa(param):
    return need_cache_data_aa.get(param, [])

@cacheable.ProcessWiseCache.cache('name_bb', capacity=100, timeout=60, deref=False)
def cache_bb(param):
    return need_cache_data_bb.get(param, [])

```

 arguments:

-   `name`: for distinguishing `cacheable.ProcessWiseCache` objects, if not exist, init a new object and save it, otherwise use exist one

-   `capacity`: `capacity` of `LRU`, for init a `LRU` object

-   `timeout`: `timeout` of `LRU`, for init a `LRU` object

-   `deref`: deepcopy or reference of the cache data
    - `True`: deepcopy of cache data
    - `False`: reference of cache data

-   `key_extractor`: `LRU.__setitem__ and LRU.__getitem__` `key` generating function, if `None` use the default method `cacheable.ProcessWiseCache.arg_str(args, argkv)`

	```
    # args is `tuple`, argkv is `dict`
    def my_key_extractor(args, argkv):
        return str(args) + str(argkv)

    need_cache_data = {'key': 'data'}

    # `my_key_extractor` use `param` generate `LRU.__setitem__, LRU.__getitem__` `key`
    # the decorator function use `key` checks whether the data has been cached or not
    @cacheable.ProcessWiseCache.cache('cache_key', capacity=100, timeout=60,
                                      deref=False, key_extractor=my_key_extractor)
    def cache_data(a, b, c):
        return need_cache_data.get('key', 'default_data')

    # `args`=('key1', 'key2') `argkv`={'c': 'key3'}
    data = cache_data('key1', 'key2', c='key3')
	```

return: a decorator function. It checks whether the data has been cached, if not or has been timeout, cache and return the data.

# Author

Baohai Liu(刘保海) <baohai.liu@baishancloud.com>

# Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Baohai Liu(刘保海) <baohai.liu@baishancloud.com>
