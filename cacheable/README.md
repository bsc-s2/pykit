<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [cacheable.LRU](#cacheablelru)
  - [cacheable.ProcessWiseCache](#cacheableprocesswisecache)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

# Name

cacheable.

Cache data which access frequently.

# Status

The library is considered production ready.

# Synopsis

```
from pykit import cacheable

@cacheable.ProcessWiseCache.cache( 'key', capacity = 100, timeout = 5 * 60, deref = False )
def test_fun( name ):
    return name

print test_fun( 'test' )

lc = cacheable.LRU(2, 10)
lc['key'] = 'val'

print lc['key']
```

# Description


# Methods

## cacheable.LRU

 syntax :

`cacheable.LRU(capacity, timeout=60)`

 arguments :

-   `capacity`:
    - the lru capacity

-   `timeout`:
    - max effective time

## cacheable.ProcessWiseCache

 syntax :

`cacheable.ProcessWiseCachecache.cache(name, capacity = 100, timeout = 60, deref=True, ismethod=False, keyExtractor = None)`

cache your fun return val

 arguments :

-   `name`:
    - cache name

-   `capacity`:
    - the max size of the cache

-   `timeout`:
    - max effective cache time

-   `deref`:
    - True:the deepcopy cache val 
    - False:the cache val ref

-   `ismethod`:
    - True:use mem_cache_wrapper 
    - False:use cache_wrapper

-   `KeyExtractor`:
    - the cache dict key create fun, None:use the default fun

# Author

Baohai Liu(刘保海) <baohai.liu@baishancloud.com>

# Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Baohai Liu(刘保海) <baohai.liu@baishancloud.com>
