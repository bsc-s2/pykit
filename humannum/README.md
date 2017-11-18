<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [humannum.humannum](#humannumhumannum)
  - [humannum.parsenum](#humannumparsenum)
  - [humannum.parseint](#humannumparseint)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

humannum

Convert number to human readable format in a string.

#   Status

This library is considered production ready.

#   Synopsis

```python
from pykit import humannum
print humannum.humannum({
    'total': 10240,
    'progress': [1, 1024*2.1, 1024*3.2],
})
# {"total" : "10K", "progress" : [1, "2.1K", "3.2K"]}
```

#   Description

Convert numbers(or numbers in `dict` or `list`) to human readable format in
string.

#   Methods

##  humannum.humannum

**syntax**:
`humannum.humannum(data, unit=None, include=None, exclude=None)`

**arguments**:

-   `data`:
    could be a primitive type: `int` or `float`,
    or a non-primitive type object `list` or `dict`.

    -   For primitive type like `int`, it converts it to string.
    -   For non-primitive type like `dict`, it traverse recursively over all
        of its fields and convert them to string.

-   `unit`:
    specifies the unit of the number in the result string.
    It could be one of: `1024`(K), `1024^2`(M) ... `1024^8`(Y).

    If it is None, a proper unit will be chosen to output the shortest string.
    For example, for `102400` it chooses `K`. For `10240000` it chooses `M`.

-   `include`:
    specifies to convert only a subset of the keys of a `dict` `data`.
    It could be a `list`, `tuple` or `set` of keys.

    -   It has no effect on a primitive `data`.
    -   It is not passed to sub `dict` or `list`.

-   `exclude`:
    specifies **NOT** to convert some of the keys of a `dict` `data`.
    It could be a `list`, `tuple` or `set` of keys.

    -   It has no effect on a primitive `data`.
    -   It is not passed to sub `dict` or `list`.


**return**:
-   For a primitive type data, it returns a string representing the number.
-   For a `dict` or `list`, it makes a duplicate of `data` and convert its
    number fields.
    It leaves the original `data` intact.

##  humannum.parsenum

**syntax**:
`humannum.parsenum(data, safe=None)`

Parse humanized number string like `10.5K` to `int` or `float`.
It also parses percentage number to `float`.

```python
print humannum.parsenum('1.01k')
# 10342.4
print humannum.parsenum('10.3%')
# 0.103
```

**arguments**:

-   `data`:
    number string.

    Valid units are:
    `k`, `m`, `g`, `t`, `p`, `e`, `z` and `y`.
    Suffix `b` and `i` will be ignored.
    For example: `10.1K`, `10.1k`, `10.1Kb` and `10.1Ki` are all the same.

    For percentage number, valid unit is `%`.
    For example: `10.1%`.

-   `safe`:
    if `safe` is `True` and data is not a valid number string, it silently
    returns the original `data`, instead of raising an `ValueError`.

    By default it is `False`.

**return**:
a `int` number or `float` number.


## humannum.parseint

**syntax**:
`humannum.parseint(data, safe=None)`

Same as `humannum.parsenum` but it always casts result to a `int` number.


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
