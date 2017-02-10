<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [cachepool.CachePool](#cachepoolcachepool)
  - [cachepool.make_wrapper](#cachepoolmake_wrapper)
  - [cachepool.CacheWrapper](#cachepoolcachewrapper)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


# Name

cachepool.

Reusable in-process object cache in process.

#   Status

This library is considered production ready.

#   Synopsis

```python

from cachepool import (
    make_wrapper,

    CachePool,
    CacheWrapper,

    CachePoolError,
    CachePoolGeneratorError,
)

# object could be reused in process
class Element(object):

    def __init__(self, *args, **argkw):
        self.args = args
        self.argkw = argkw

        self.closed = False

    def close(self):
        self.closed = True

    def do(self):
        print self.args
        print self.argkw

# element generator
def generator(*args, **argkw):
    return Element(*args, **argkw)

# close element when pool is full or the element is broken
def close_callback(element):
    element.close()

# decide whether the element can be reused or not when error occurs
def reuse_decider(errtype, errval, _traceback):
    if errtype in (CachePoolError, CachePoolGeneratorError):
        return True

    return False

# create pool with wrapper
pool = CachePool(
    generator,
    generator_args=[],
    generator_argkw={},
    close_callback=close_callback,
    pool_size=512,
)

wrapper = make_wrapper(
    pool,
    reuse_decider=reuse_decider,
)


with wrapper() as ele:
    ele.do()

# get statistics about pool
stat = pool.stat
# stat = {'new': 1,
#         'get': 1,
#         'put': 1,
#         }
```

#   Description

#   Methods

##  cachepool.CachePool

**syntax**:
```
pool = cachepool.CachePool(
    generator,
    generator_args=[1, 2, 'x'],
    generator_argkw={'key': 'value', (1, 2): '1 and 2'},
    close_callback=lambda element: element.close(),
    pool_size=512,
)
```

Create a pool: `pool`.
Reusable elements are maintained in pool.

**arguments**:

-   `generator`:

    function to generate new element:

    ```
    def generator(*args, **argkw):
        return Element(*args, **argkw)
    ```

-   `generator_args`:

    list parameters of generator, default is `None`

    ```
    [1, 2, 'x']
    ```

-   `generator_argkw`:

    dict parameters of generator, default is `None`

    ```
    {
        'key': 'value',
        (1, 2): '1 and 2',
    }
    ```

-   `close_callback`:

    close element when `pool` is full or the element is broken, default is `None`

    ```
    def close_callback(element):
        element.close()
    ```

-   `pool_size`:

    pool size, default is `1024`

    ```
    512
    ```

**return**:
an instance of `cachepool.CachePool()`, that can be used to get an element
by calling the `get()` method of the `cachepool.CachePool()` instance.

New element will be created by `generator` if the `pool` is empty,
otherwise we just use a cached element.

##  cachepool.make_wrapper

**syntax**:
`cachepool.make_wrapper(pool, reuse_decider=None)`

Create a wrapper function that return a `cachepool.CacheWrapper` instance.
Example:

```
wrapper = cachepool.make_wrapper(
    pool,
    reuse_decider=reuse_decider,
)

with wrapper() as elt:
    print elt
```

**arguments**:

-   `pool`:

    pass to cachepool.CacheWrapper

-   `reuse_decider`:

    pass to cachepool.CacheWrapper

**return**:
a function whose return value is a `cachepool.CacheWrapper` instance, which
can be executed with the `with` statement.

##  cachepool.CacheWrapper

**syntax**:
```
wrapper = cachepool.CacheWrapper(
    pool,
    reuse_decider=reuse_decider,
)
```

Create a wrapper: `wrapper` which can be executed with the `with` statement.

**arguments**:

-   `pool`:

    an instance of cachepool.CachePool

-   `reuse_decider`:

    function that runs when error occurs in `with`
    -   return `True` means reuse
    -   return `False` means drop

    ```
    def reuse_decider(errtype, errval, _traceback):
        if errtype in (CachePoolError, CachePoolGeneratorError):
            return True

        return False
    ```

**return**:
an instance of `cachepool.CacheWrapper`, which can be executed with the `with`
statement.


#   Author

Slasher Liang (梁辰风) <mcq.sejust@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2016 Slasher Liang (梁辰风) <mcq.sejust@gmail.com>
