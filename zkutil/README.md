<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Methods](#methods)
  - [zkutil.lock_id](#zkutillock_id)
  - [zkutil.parse_lock_id](#zkutilparse_lock_id)
  - [zkutil.make_digest](#zkutilmake_digest)
  - [zkutil.make_acl_entry](#zkutilmake_acl_entry)
  - [zkutil.perm_to_long](#zkutilperm_to_long)
  - [zkutil.perm_to_short](#zkutilperm_to_short)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


#   Name

zkutil

#   Status

This library is still in beta phase.

#   Description

Some helper function to make life easier with zookeeper.

#   Methods

##  zkutil.lock_id

**syntax**:
`zkutil.lock_id(node_id=None)`

It builds a string used as zk lock node value, to describe lock holder's
information.

The result string is in form:

```
<node_id>-<ip>-<process_id>-<counter>

# e.g. web-192.168.0.2-1233-0000000001
```

`ip` is chosen from all local ipv4.
If there is an intra net ip, use it.
Otherwise, use an public ip it found.

**arguments**:
-   `node_id`:
    is an arbitrary string representing a host.

    If it is `None`, `config.zk_node_id` is used.

**return**:
a string for lock identifier.

## zkutil.parse_lock_id

**syntax**:
`zkutil.parse_lock_id(data_str)`

It parse string built by `zkutil.lock_id()` to an dictionary.

**arguments**:
-   `data_str`:
    string built by `zkutil.lock_id()`.

**return**:
```python
{
    "node_id": "<node_id>",
    "ip": "<ip>",
    "process_id": process_id,
}
```

`process_id` is an `int`, the other two are `string`s.

If any of these three field can not be parsed correctly, it will be `None`.

##  zkutil.make_digest

**syntax**:
`zkutil.make_digest(acc)`

It make a digest for string acc

The `acc` string is in form:

```
username:password

```

**return**:
a digest string.


##  zkutil.make_acl_entry

**syntax**:
`zkutil.make_acl_entry(username, password, permissions)`

It concat `username`, `digest` and `permissions` to a string as acl entry.

**arguments**:
-   `username`:
    the name of zookeeper user.

-   `password`:
    the password of zookeeper user.

-   `permissions`:
    a string, a list or a tuple.
    each element in `permissions` is a char who should be included in `cdrwa`. If `permissions` contains extra element, `PermTypeError` will be raised.

**return**
    a string in form:
```
"digest:<username>:<digest>:<permissions>"
```
where `digest` is a string build by `zkutil.make_digest()`


##  zkutil.perm_to_long

**syntax**:
`zkutil.perm_to_long(short, lower=True)`

Convert short style zookeeper permissions(`cdrwa` or `CDRWA`)
to standard permission list(`['create', 'delete', 'read', 'write', 'admin']`).

**arguments**:

-   `short`:
    is `iterable` of short permissions that can be used in `for-loop`.
    Such as `"cdrw"` or `['c', 'd']`

-   `lower`:
    specifies if convert result to lower or upper case.
    By default it is `True`, for lower case.

**return**:
a list of standard permission.


##  zkutil.perm_to_short

**syntax**:
`zkutil.perm_to_short(lst, lower=True)`

The reverse of `perm_to_long`:
It convert a list of standard permissions back to a short permission string,
such as `cdrw`.

**arguments**:

-   `lst`:
    is a list of standard permissions, such as `['create', 'read']`.

-   `lower`:
    specifies if convert result to lower or upper case.
    By default it is `True`, for lower case.

**return**:
a string of short permissions.


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
