<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Methods](#methods)
  - [mysqlutil.gtidset.compare](#mysqlutilgtidsetcompare)
  - [mysqlutil.gtidset.dump](#mysqlutilgtidsetdump)
  - [mysqlutil.gtidset.load](#mysqlutilgtidsetload)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

mysqlutil

#   Status

This library is considered production ready.

#   Description

Mysql related datatype, operations.

#   Methods


##  mysqlutil.gtidset.compare

**syntax**:
`mysqlutil.gtidset.compare(a, b)`

Compares two gtidset dictionary and returns the differences.

**arguments**:

-   `a`:
    is a gtidset dictionary, built from `mysqlutil.gtidset.load`.

-   `b`:
    is a gtidset dictionary, built from `mysqlutil.gtidset.load`.

**return**:
a dictionary that describes what gtid is on left side(`a`) only and what gtid is
on right side(`b`) only.

The item `onlyleft` or `onlyright` is a `rangeset.IntIncRangeSet` representing
the gtid range which is on left(right) only, for each uuid.

If there are not any gtid absent on the right side, `onlyleft` is `{"length":0,
"gtidset": {}}` and vice versa:

```
{
    "onlyleft": {
        'length': 45,
        'gtidset': {
            "103a96e9-a030-11e6-b082-a0369fabbda4": [[25, 25]],
            "3f96fb31-6a18-11e6-bd74-a0369fabbdb8": [[1, 30]],
            "630b605d-9ec7-11e6-aae9-a0369fabbdb8": [[1, 4]],
            "83e2adaf-9c37-11e6-9d6e-a0369fb6f7b4": [[61, 70]]
        },
    },
    "onlyright": {
        'length': 81,
        'gtidset': {
            "103a96e9-a030-11e6-b082-a0369fabbda4": [[26, 26]],
            "f4ebb415-a801-11e6-9079-a0369fb4eb00": [[1, 80]]
        },
    },
}
```


##  mysqlutil.gtidset.dump

**syntax**:
`mysqlutil.gtidset.dump(gtidset, line_break='\n')`

Dump gtidset dictionary to string.
See `mysqlutil.gtidset.load`.

**arguments**:

-   `gtidset`:
    is the gtidset dictionary to dump.

-   `line_break`:
    specifies additional separator after "," for each uuid set.
    By default it is `"\n"`.

**return**:
gtidset string.


##  mysqlutil.gtidset.load

**syntax**:
`mysqlutil.gtidset.load(gtidset_str)`

Loads gtidset string and parse it into a dictionary.
The key in the dictionary is the uuid of a mysql instance.
The value is a `rangeset.IntIncRangeSet` instance represents gtid set.

**arguments**:

-   `gtidset_str`:
    is the raw gtidset string read from mysql command, such as
    `Retrieved_Gtid_Set` or `Executed_Gtid_Set` in `show slave status`:

    ```
    Retrieved_Gtid_Set: 9dd98013-a885-11e6-9c9d-a0369fb4eb00:3662619777-3663056053

    Executed_Gtid_Set: 25061445-9f18-11e6-8572-a0369fabbdb8:1-1245974985,
    9dd98013-a885-11e6-9c9d-a0369fb4eb00:1-3663056053,
    dfe3bcd6-6a0f-11e6-82e5-a0369fabbdf0:1-41001
    ```

**return**:
a dictionary in the following format:

```
mysqlutil.gtidset.load(
    '103a96e9-a030-11e6-b082-a0369fabbda4:1-20:25,\n'
    '3f96fb31-6a18-11e6-bd74-a0369fabbdb8:1-30,\n'
    '630b605d-9ec7-11e6-aae9-a0369fabbdb8:1-90,\n'
    '83e2adaf-9c37-11e6-9d6e-a0369fb6f7b4:1-70')

{
    '103a96e9-a030-11e6-b082-a0369fabbda4' : [[1,20], [25, 25]],
    '3f96fb31-6a18-11e6-bd74-a0369fabbdb8' : [[1,30]],
    '630b605d-9ec7-11e6-aae9-a0369fabbdb8' : [[1,90]],
    '83e2adaf-9c37-11e6-9d6e-a0369fb6f7b4' : [[1,70]],
}
```




#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
