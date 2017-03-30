<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Methods](#methods)
  - [zkutil.lock_data](#zkutillock_data)
  - [zkutil.parse_lock_data](#zkutilparse_lock_data)
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

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
