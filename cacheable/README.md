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
  - [LRU.__setitem__](#cacheablesetitem)
  - [LRU.__getitem__](#cacheablegetitem)
  - [cacheable.ProcessWiseCache.cache](#cacheableprocesswisecache)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

# Name

cacheable

Cache info which access frequently.

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

cache_info = {'key': [1, 2]}

def get_cache_info(param):

    return cache_info.get(param, [])

# define the function with a decorator
@cacheable.ProcessWiseCache.cache('cache_key', capacity=100, timeout=60, deref=False)
def get_info(param):
    return get_cache_info(param)

# when first call the function the return val will be cached
get_info = get_info('key')

# later if call the function use the same param again, the return val will be got from cache
time.sleep(30)
get_info = get_info('key')

# if item timeout in `LRU`, when call the function the info will be cached again
time.sleep(70)
get_info = get_info('key')

# decorate a function of a class
class CacheClass(object):

    @cacheable.ProcessWiseCache.cache('cacher_name', capacity=10240, timeout=5 * 60, deref=True)
    def get_info(self, param):
        return get_cache_info(param)

tt = CacheClass()
tt.get_info('key')

```

# Description

# Classes

## cacheable.LRU

 syntax: `cacheable.LRU(capacity, timeout=60)`

 Least Recently Used Cache.

 arguments:

-   `capacity`: capacity of LRU, when the size of LRU is greater than `capacity` * 1.5, older item will be cleaned until the size is equal to `capacity`

-   `timeout`: max cache time of item, unit is second, default is 60

# Methods

## LRU.__getitem__

syntax: `LRU.__getitem__(key)`

Get cache info from LRU.

If exist, move it to the tail of LRU to avoid to be cleaned, then return the val and item old status.

If timeout, delete it and raise `KeyError`.

if not exist, raise `KeyError`.

arguments:

- `key`: key of the cache item

return: two values

- one is cache val
- another is item old status(`True`: it is old, `False`: it is new).

```
 c = cacheable.LRU(10, 10)
 c['a'] = 'val_a'

 # old is `False`
 try:
    (val, old) = c['a']
 except:
    print('key error')

 # exist time more than half of `timeout` old is `True`
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

Insert cache info into the tail of LRU to avoid to be cleaned.

After insert, if size of LRU is greater than `capacity` * 1.5, clean old items until size is equal to `capacity`

 ```
 c = cacheable.LRU(2, 60)

 # insert new item to the tail of LRU
 c['a'] = 'val_a'
 c['b'] = 'val_b'
 c['c'] = 'val_c'
 
 # after insert `d`, `a` and `b` will be cleaned
 c['d'] = 'val_d'

 ```

arguments:

 - `key`: as key of the `dict` in LRU

 - `val`: need cached val

return: nothing

## cacheable.ProcessWiseCache.cache

 syntax:`cacheable.ProcessWiseCache.cache(name, capacity=1024 * 4, timeout=60, deref=True, key_extractor=None)`

 It is a classmethod, init cacher and create LRU object.

 arguments:

-   `name`: cacher name, if not exist the cacher, use it as `dict` key create a new cacher, otherwise, use exist one

-   `capacity`: `capacity` of `LRU`

-   `timeout`: `timeout` of `LRU`

-   `deref`: deepcopy or ref of the cache info(`True`: deepcopy of cache info, `False`: ref of cache info)

-   `key_extractor`: LRU `__setitem__` key create function, if `None` use the default method `cacheable.ProcessWiseCache.arg_str`

	```
    # args is `list`, argkv is `dict`
    def my_key_extractor(args, argkv):
        return str(args) + str(argkv)

    # `my_key_extractor` use `param1`, `param`' as params create LRU `__setitem__` key
    @cacheable.ProcessWiseCache.cache('cache_key', capacity=100, timeout=60,
                                      deref=False, key_extractor=my_key_extractor)
    def cache_info(param1, param2):
       return 'info'
	```

return: a decorator. Define a method with the decorator, it check cache info, if timeout or not exist, insert into cacher. Then return the cache info.

# Author

Baohai Liu(刘保海) <baohai.liu@baishancloud.com>

# Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Baohai Liu(刘保海) <baohai.liu@baishancloud.com>
