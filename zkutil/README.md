<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Methods](#methods)
  - [zkutil.lock_data](#zkutillock_data)
  - [zkutil.parse_lock_data](#zkutilparse_lock_data)
  - [zkutil.make_digest](#zkutilmake_digest)
  - [zkutil.make_acl_entry](#zkutilmake_acl_entry)
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

##  zkutil.lock_data

**syntax**:
`zkutil.lock_data(node_id)`

It builds a string used as zk lock node data, to describe lock holder's
information.

The result string is in form:

```
<node_id>-<ip>-<process_id>

# e.g. web-192.168.0.2-1233
```

`ip` is chosen from all local ipv4.
If there is an intra net ip, use it.
Otherwise, use an public ip it found.

**arguments**:
-   `node_id`:
    is an arbitrary string representing a host.

**return**:
a string for lock data.

## zkutil.parse_lock_data

**syntax**:
`zkutil.parse_lock_data(data_str)`

It parse string built by `zkutil.lock_data()` to an dictionary.

**arguments**:
-   `data_str`:
    string built by `zkutil.lock_data()`.

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

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
