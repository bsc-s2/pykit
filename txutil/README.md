<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Exceptions](#exceptions)
  - [CASConflict](#casconflict)
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

#   Exceptions

##  CASConflict

**syntax**:
`CASConflict()`

User should raise this exception when a CAS conflict detect in a user defined
`set` function.


#   Classes

##  CASRecord

**syntax**:
`CASRecord(v, stat, n)`

The class of a record yielded from `txutil.cas_loop()`.
It has 3 attributes `v`, `stat` and `n`.

`v` stores the value and the `stat` stores value stat information that is used
to identify in `setter` whether the stat changed.

`n` is the number of times it CAS runs.
The first time `n` is 0.


#   Methods

##  txutil.cas_loop

**syntax**:
`txutil.cas_loop(getter, setter, args=(), kwargs=None, conflicterror=CASConflict)`

A helper generator for doing CAS(check and set or compare and swap).
See [CAS](https://en.wikipedia.org/wiki/Compare-and-swap)

A general CAS loop is like following(check the version when update):

```python
while True:
    curr_val, stat = getter(key="mykey")
    new_val = curr_val + ':foo'
    try:
        setter(new_val, stat, key="mykey")
    except CASConflict:
        continue
    else:
        break
```

`cas_loop` simplifies the above workflow to:

```python
for curr in cas_loop(getter, setter, args=("mykey", )):
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

        def _get(self, db, key, **kwargs):
            # db, key == 'dbname', 'mykey'
            with self.lock:
                return self.val, self.ver

        def _set(self, db, key, val, prev_stat, **kwargs):
            # db, key == 'dbname', 'mykey'
            with self.lock:
                if prev_stat != self.ver:
                    raise CASConflict(prev_stat, self.ver)

                self.val = val
                self.ver += 1

        def test_cas(self):

            for curr in txutil.cas_loop(self._get, self._set, args=('dbname', 'mykey', )):
                curr.v += 2

            print((self.val, self.ver)) # (2, 1)
    ```

-   `args` and `kwargs`:
    optional positioned arguments and key-value arguments that will be passed to `getter` and `setter`.
    By default it is an empty tuple `()` and `None`.

-   `conflicterror`:
    specifies what raised error indicating a CAS conflict, instead of using the
    default `CASConflict`.

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
