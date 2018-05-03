<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [cluster.make_server_id](#clustermake_server_id)
  - [cluster.validate_server_id](#clustervalidate_server_id)
  - [cluster.make_serverrec](#clustermake_serverrec)
  - [cluster.get_serverrec_str](#clusterget_serverrec_str)
  - [cluster.make_drive_id](#clustermake_drive_id)
  - [cluster.parse_drive_id](#clusterparse_drive_id)
  - [cluster.validate_drive_id](#clustervalidate_drive_id)
  - [cluster.validate_idc](#clustervalidate_idc)
  - [cluster.idc_distance](#clusteridc_distance)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

cluster

#   Status

The library is considered production ready.

#   Synopsis

```python
from pykit import cluster

server_id = cluster.make_server_id()
# 12 chars from primary MAC addr: "c62d8736c728"

is_valid = cluster.validate_server_id(server_id)
# return True or False

serverrec = cluster.make_serverrec('.l1', 'center', {'role1': 1})
# out:
#{
#   'cpu': {
#       'count': 1,
#       'frequency': 2200
#   },
#   'hostname': 'host name',
#   'idc': '.l1',
#   'idc_type': 'center',
#   'inn_ips': ['192.168.0.1'],
#   'memory': 3975237632,
#   'mountpoints': {
#       '/': {'capacity': 42140499968, 'fs': 'ext3'},
#       '/s2/drive/001': {'capacity': 5358223360, 'fs': 'xfs'},
#       '/s2/drive/002': {'capacity': 5358223360, 'fs': 'xfs'}
#   },
#   'pub_ips': ['118.1.1.1'],
#   'roles': {'role1': 1},
#   'server_id': '00163e0630f7'
#}
```

#   Description

Some helper function for the server in a cluster.

#   Methods

##  cluster.make_server_id

**syntax**:
`cluster.make_server_id()`

Identifies a server.

**return**:
A string, Format: 12 chars from primary MAC addr(e.g.: "c62d8736c728").

##  cluster.validate_server_id

**syntax**:
`cluster.validate_server_id(server_id)`

Check a server_id is valid or not.

**arguments**:

-   `server_id`:
    The server_id which will be checked.

**return**:
`True` or `False`, means the server_id is valid or not.

##  cluster.make_serverrec

**syntax**:
`cluster.make_serverrec(idc, idc_type, roles, **argkv)`

Make a `dict` (a server record).

-   Collected physical field(pub_ips, inn_ips, hostname, server_id, memory, cpu).

-   User specified field(idc, idc_type, roles(as a dict whose values are 1), other fields if needed).

-   Mounted path(mount path, capacity, fs type).

**arguments**:

-   `idc`:
    The name of a idc in the cluster. Format: `.l1-name.l2-name...`.

-   `idc_type`:
    Type of the idc.

-   `roles`:
    A `dict` whose values are `1`, the roles in the server.

-   `argkv`:
    Other fields if needed.

**return**:
A `dict`, like:

```
{
    'cpu': {
        'count': 1,
        'frequency': 2200
    },
    'hostname': 'host name',
    'idc': '.l1',
    'idc_type': 'center',
    'inn_ips': ['192.168.0.1'],
    'memory': 3975237632,
    'mountpoints': {
        '/': {'capacity': 42140499968, 'fs': 'ext3'},
        '/s2/drive/001': {'capacity': 5358223360, 'fs': 'xfs'},
        '/s2/drive/002': {'capacity': 5358223360, 'fs': 'xfs'}
    },
    'pub_ips': ['118.1.1.1'],
    'roles': {'role1': 1},
    'server_id': '00163e0630f7'
}
```

##  cluster.get_serverrec_str

**syntax**:
`cluster.get_serverrec_str(serverrec)`

Collect some important info(`server_id`, `idc`, `idc_type`, `roles`,
`mountpoints_count`) of `serverrec` into a `str`.

**arguments**:

-   `serverrec`:
    The server record return from `cluster.make_serverrec`.

**return**:
A `str`, like:

```
"server_id: 00aabbccddee; idc: .l1; idc_type: zz; roles: {'role1': 1}; mountpoints_count: 3"
```

##  cluster.make_drive_id

**syntax**:
`cluster.make_drive_id(server_id, mount_point_index)`

Make a `drive_id` which identifies a disk drive.

**arguments**:

-   `server_id`:
    A string, Format: 12 chars from primary MAC addr

-   `mount_point_index`:
    It is a 3-digit mount path, `001` for `/drives/001`.

**return**:
The drive id `<server_id>0<mount_point_index>`, Format: 16 chars.

##  cluster.parse_drive_id

**syntax**:
`cluster.parse_drive_id(drive_id)`

Parse drive_id into a dict that contains separated fields.

**arguments**:

-   `drive_id`:
    A string, Format: 16 chars `<server_id>0<mount_point_index>`.

**return**:
A `dict` like:

```
{
    'server_id': 'aabbccddeeff',
    'mount_point_index': 10,
}
```

##  cluster.validate_drive_id

**syntax**:
`cluster.validate_drive_id(drive_id)`

Check a `drive_id` is valid or not.

**arguments**:

-   `drive_id`:
    A string, Format: 16 chars `<server_id>0<mount_point_index>`.

**return**:
`True` or `False`, means the `drive_id` is valid or not.

##  cluster.validate_idc

**syntax**:
`cluster.validate_idc(idc)`

Check the name of a idc is valid or not.

**arguments**:

-   `idc`:
    The name of a idc in the cluster. Format: `.l1-name.l2-name...`.

**return**:
`True` or `False`, means the name is valid or not.

##  cluster.idc_distance

**syntax**:
`cluster.idc_distance(idc_a, idc_b)`

Estimate distance between two idc.

**arguments**:

-   `idc_a`:
    First idc name.

-   `idc_b`:
    Second idc name.

**return**:
The distance of them.

#   Author

Baohai Liu(刘保海) <baohai.liu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Baohai Liu(刘保海) <baohai.liu@baishancloud.com>
