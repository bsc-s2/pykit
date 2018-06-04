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
- [Classes](#classes)
  - [cluster.BlockID](#clusterblockid)
    - [block id](#block-id)
    - [cluster.BlockID.parse](#clusterblockidparse)
    - [cluster.BlockID.`__str__`](#clusterblockid__str__)
  - [cluster.BlockGroupID](#clusterblockgroupid)
    - [block group id](#block-group-id)
    - [cluster.BlockGroupID.parse](#clusterblockgroupidparse)
    - [cluster.BlockGroupID.`__str__`](#clusterblockgroupid__str__)
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

serverrec = cluster.make_serverrec('.l1', 'center', {'role1': 1}, "/s2")
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
#   'server_id': '00163e0630f7',
#   'next_mount_index': 1,
#   "allocated_drive": {
#       "/s2/dirve/001": {"status": "normal",},
#       "/s2/dirve/002": {"status": "normal",},
#   },
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
`cluster.make_serverrec(idc, idc_type, roles, allocated_drive_pre, **argkv)`

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

-   `allocated_drive_pre`:
    Init status(`normal`) of the mountpoint which startswith it.

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
    'next_mount_index': 1,
    "allocated_drive": {
        "/s2/dirve/001": {"status": "normal",},
        "/s2/dirve/002": {"status": "normal",},
    },
}
```

##  cluster.get_serverrec_str

**syntax**:
`cluster.get_serverrec_str(serverrec)`

Collect some important info(`server_id`, `idc`, `idc_type`, `roles`,
`mountpoints_count`, `allocated_drive_count`) of `serverrec` into a `str`.

**arguments**:

-   `serverrec`:
    The server record return from `cluster.make_serverrec`.

**return**:
A `str`, like:

```
"server_id: 00aabbccddee; idc: .l1; idc_type: zz; roles: {'role1': 1}; mountpoints_count: 3; allocated_drive_count: 0"
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

#   Classes

##  cluster.BlockID

**syntax**:
`BlockID(namedtuple('_BlockID', 'type block_group_id block_index drive_id pg_seq'))`

Parse or generate block id.

### block id

`block_id`: identifies a single data or parity block.

A block is a single file on disk that contains multiple user-file.

Format: 47 chars

```
(d|p|x)<block_group_id><block_index><drive_id><pg_seq>
1      16              4            16        10
```

Example: `d g000630000000123 0101 c62d8736c7280002 0000000001`(without
space)

-   `type`:

    -   `d`(data) for a `data_block`.

    -   `p`(parity) for a in-IDC `parity_block`.

    -   `x`(xor-parity) for a cross-IDC `parity_block`.

-   `block_group_id`:
    to which block group this block belongs.

-   `block_index`:
    specifies the block position in a `block_group`.
    It is a 4 digit decimal `number`:

    -   The first 2 digits is the IDC index.

    -   The latter 2 digits is the position in a IDC.

    Both these 2 parts starts from 00.

    E.g.: `block_index` of the 1st block in the first IDC is: `0000`.
    `block_index` of the 2nd block in the 3rd IDC is: `0201`.

-   `drive_id`:
    specifies the disk drive where this block resides.

-   `pg_seq`:
    is a block group wise monotonic incremental id.
    To ensure that any two blocks have different `block_id`.

### cluster.BlockID.parse

**syntax**:
`cluster.BlockID.parse(block_id)`

A class method. Parse `block_id` from string to `BlockID` instanse.
If `block_id` length is wrong, `BlockIDError` raises.

**arguments**:

-   `block_id`
    block_id in string

**return**:
A `cluster.BlockID` instance

### cluster.BlockID.`__str__`

**syntax**:
`cluster.BlockID.__str__()`

Rewrite `__str__`, convert `self` to `block_id` string.

**return**:
A `block_id`.

```python
block_id = 'dg0006300000001230101c62d8736c72800020000000001'

# test parse()
bid = cluster.BlockID.parse(block_id)
print bid.type            # d
print bid.block_group_id  # g000630000000123
print bid.block_index     # 0101
print bid.drive_id        # c62d8736c7280002
print bid.pg_seq          # 0000000001

# test __str__()
print bid                 # dg0006300000001230101c62d8736c72800020000000001
```

##  cluster.BlockGroupID

**syntax**:
`BlockGroupID(namedtuple('_BlockGroupID', 'block_size seq'))`

Parse or generate block group id.

### block group id

`block_group_id`: identifies a block group.

A block group is responsible of managing a group of blocks and block replication.

Format: 16 char

```
g<block_size_in_gb><seq>
 5 digit           10 digit
```

-   `block_size_in_gb`: 6 digit indicates max block size in this block group.
    Right padding with 0.

    > Thus the largest block is 99999 GB.

-   `seq`:
    zookeeper generates incremental sequence number. 10 digit, e.g.: `0000000001`.

    A `seq` is unique in a cluster.

Example: `g 00064 0000000123`(without space).

### cluster.BlockGroupID.parse

**syntax**:
`cluster.BlockGroupID.parse(block_group_id)`

A class method. Parse `block_group_id` from string to `BlockGroupID` instanse.
If `block_group_id` length is wrong, `BlockGroupIDError` raises.

**arguments**:

-   `block_group_id`
    block_group_id in string

**return**:
A `cluster.BlockGroupID` instance

### cluster.BlockGroupID.`__str__`

**syntax**:
`cluster.BlockGroupID.__str__()`

Rewrite `__str__`, convert `self` to `block_group_id` string.

**return**:
A `block_group_id`.

```python
block_group_id = 'g000640000000123'

# test parse()
bgid = cluster.BlockGroupID.parse(block_group_id)
print bgid.block_size  # 00064
print bgid.seq         # 0000000123

# test __str__()
print bgid             # g000640000000123
```

#   Author

Baohai Liu(刘保海) <baohai.liu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Baohai Liu(刘保海) <baohai.liu@baishancloud.com>
