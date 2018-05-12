<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Classes](#classes)
  - [CASRecord](#casrecord)
- [Methods](#methods)
  - [txutil.cas_loop](#txutilcas_loop)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


#   Name

txutil

#   Status

This library is considered production ready.

#   Description

A collection of helper functions to implement transactional operations.

#   Classes

##  CASRecord

**syntax**:
`CASRecord(v, stat)`

The class of a record yielded from `txutil.cas_loop()`.
It has two attribute `v` and `stat`.
`v` stores the value and the `stat` stores value stat information that is used
to identify in `setter` whether the stat changed.


#   Methods

##  txutil.cas_loop

**syntax**:
`txutil.cas_loop(getter, setter, key=None)`

A helper generator for doing CAS(check and set or compare and swap).
See [CAS](https://en.wikipedia.org/wiki/Compare-and-swap)

A general CAS loop is like following(check the version when update):

```python
while True:
    curr_val, stat = getter(key)
    new_val = curr_val + ':foo'
    ok = setter(key, new_val, stat)
    if ok:
        break
```

`cas_loop` simplifies the above workflow to:

```python
for curr in cas_loop(getter, setter, key):
    curr.v += ':foo'
```

The loop body runs several times until a successful update is made(`setter` returns `True`).

**arguments**:

-   `getter`:
    is a `callable` receiving one argument and returns a tuple of `(value, stat)`.
    `stat` is any object that will be send back to `setter` for it to check
    whether stat changed after `getter` called.

-   `setter`:
    is a `callable` to check and set the changed value.

    A fine sample is:

    ```python
    class Foo(object):

    def __init__(self):
        self.lock = threading.RLock()
        self.val = 0
        self.ver = 0

        def _get(self, key):
            with self.lock:
                return self.val, self.ver

        def _set(self, key, val, prev_stat):
            with self.lock:
                if prev_stat != self.ver:
                    return False
                else:
                    self.val = val
                    self.ver += 1
                    return True

        def test_cas(self):

            for curr in txutil.cas_loop(self._get, self._set):
                curr.v += 2

            print((self.val, self.ver)) # (2, 1)
    ```

-   `key`:
    an optional argument that will be passed to `getter` and `setter`.
    By default it is `None`.

**return**:
a `generator` that yields a `CASRecord` for user to update its attribute `v`.
If a user modifies `v`, an attempt to update by calling `setter`  will be made.

If the update succeeds, the `generator` quits.

If the update detects a conflict, it yields a new `CASRecord` and repeat the
update.


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
