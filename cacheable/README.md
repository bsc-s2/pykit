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

Cache data which access frequently.

# Status

The library is considered production ready.

# Synopsis

LRU:

```

from pykit import cacheable

c = cacheable.LRU(10, 60)
c['key'] = 'val'

# exist time more than half of the timeout, old=`True`
# if timeout, raise `KeyError`
try:
    (val, old) = c['key']
except KeyError:
    ...

```
ProcessWiseCache:

```

from pykit import cacheable

cache_info = {'param': [1, 2]}

def get_cache_info(param):

    ret = []
    if cache_info.has_key(param):
        ret = cache_info[param]
    return ret

# define the fun with a decorator
@cacheable.ProcessWiseCache.cache('cache_key', capacity=100, timeout=60, deref=False)
def fun(param):
    return get_cache_info(param)

# when first call the fun the return val will be cached
get_info = fun('param')

# later if call the fun use the same param again, the return val will be got from the cache
time.sleep(30)
get_info = fun('param')

# if item timeout in `LRU`, when call the fun the info will be cached again
time.sleep(70)
get_info = fun('param')

# decorate a fun of a class. like below
class TestMem(object):

    @cacheable.ProcessWiseCache.cache('cacher_name', capacity=10240, timeout=5 * 60, deref=True)
    def fun(self, param):
        return get_cache_info(param)

tt = TestMem()
tt.fun('param')

```

# Description

# Classes

## cacheable.LRU

 syntax: `cacheable.LRU(capacity, timeout=60)`

 LRU means access data recently, the probability of access it is high in the future.

 arguments:

-   `capacity`: the lru capacity
    - when the size of LRU is greater than `capacity` * 1.5, older item will be cleanup until the size is equal to `capacity`

-   `timeout`: max item effective time start from insert, unit is second, default is 60

# Methods

## LRU.__getitem__

syntax: `LRU.__getitem__(key)`

Get cache data from LRU.

If exist, move it to the tail of LRU as the newest.

arguments:

- `key`: key of the cache item

return: two values

- One is cache val, another is item old status, `True` or `False`.
- If timeout or not exist, raise `KeyError`

```
 c = cacheable.LRU(10, 10)
 c['a'] = 'val_a'

 # old is False
 try:
    (val, old) = c['a']
 except:
    ...

 # exist time more than half of `timeout` old is `True`
 time.sleep(6)
 try:
 	(val, old) = c['a']
 except:
 	...

 # if `timeout` raise `KeyError`
 time.sleep(5)
 try:
 	(val, old) = c['a']
 except KeyError:
 	...

```

## LRU.__setitem__
syntax: `LRU.__setitem__(key, val)`

Insert `val` into the tail of LRU as the newest.

 ```
 c = cacheable.LRU(10, 60)

 # insert two item, the second item will in the tail as the newest one
 c['a'] = 'val_a'
 c['b'] = 'val_b'

 ```

arguments:

 - `key`: use it as the key of `dict`

 - `val`: need cached val

return: nothing

## cacheable.ProcessWiseCache.cache

 syntax:`cacheable.ProcessWiseCache.cache(name, capacity=1024 * 4, timeout=60, deref=True, key_extractor=None)`

 It is classmethod, init cacher and create LRU object.

 arguments:

-   `name`: cache name

    - If not exist the cacher, use the `name` as `dict` key create a new cacher, otherwise, use exist one

-   `capacity`: `capacity` of `LRU`

-   `timeout`: `timeout` of `LRU`

-   `deref`: deepcopy or ref of the cache data

    - `True`: deepcopy of cache data

    - `False`: ref of cache data

-   `key_extractor`: LRU `__setitem__` key create fun, if `None` use the default method `cacheable.ProcessWiseCache.arg_str`

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

return: a decorator

- Apply the decorator to user define method.

- It check user data, if timeout or not exist, cache it. Then return the cache data.

# Author

Baohai Liu(刘保海) <baohai.liu@baishancloud.com>

# Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Baohai Liu(刘保海) <baohai.liu@baishancloud.com>
