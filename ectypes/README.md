<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Exceptions](#exceptions)
  - [ectypes.BlockNotFoundError](#ectypesblocknotfounderror)
  - [ectypes.BlockTypeNotSupported](#ectypesblocktypenotsupported)
  - [ectypes.BlockTypeNotSupportReplica](#ectypesblocktypenotsupportreplica)
  - [ectypes.BlockIndexError](#ectypesblockindexerror)
- [Methods](#methods)
  - [ectypes.make_serverrec](#ectypesmake_serverrec)
  - [ectypes.get_serverrec_str](#ectypesget_serverrec_str)
  - [ectypes.validate_idc](#ectypesvalidate_idc)
  - [ectypes.idc_distance](#ectypesidc_distance)
- [Classes](#classes)
  - [ectypes.ReplicationConfig](#ectypesreplicationconfig)
  - [ectypes.IDBase](#ectypesidbase)
    - [To declare a new ID type:](#to-declare-a-new-id-type)
  - [ectypes.IDCID](#ectypesidcid)
  - [ectypes.ServerID](#ectypesserverid)
  - [ectypes.local_server_id](#ectypeslocal_server_id)
  - [ectypes.DriveID](#ectypesdriveid)
  - [ectypes.BlockID](#ectypesblockid)
    - [block id](#block-id)
  - [ectypes.BlockIndex](#ectypesblockindex)
  - [ectypes.BlockDesc](#ectypesblockdesc)
  - [ectypes.BlockGroupID](#ectypesblockgroupid)
    - [block group id](#block-group-id)
  - [ectypes.BlockGroup](#ectypesblockgroup)
    - [block index](#block-index)
    - [ectypes.BlockGroup.get_block](#ectypesblockgroupget_block)
    - [ectypes.BlockGroup.get_free_block_indexes](#ectypesblockgroupget_free_block_indexes)
    - [ectypes.BlockGroup.mark_delete_block](#ectypesblockgroupmark_delete_block)
    - [ectypes.BlockGroup.delete_block](#ectypesblockgroupdelete_block)
    - [ectypes.BlockGroup.add_block](#ectypesblockgroupadd_block)
    - [ectypes.BlockGroup.get_block_type](#ectypesblockgroupget_block_type)
    - [ectypes.BlockGroup.get_block_idc](#ectypesblockgroupget_block_idc)
    - [ectypes.BlockGroup.get_replica_indexes](#ectypesblockgroupget_replica_indexes)
    - [ectypes.BlockGroup.classify_blocks](#ectypesblockgroupclassify_blocks)
    - [ectypes.BlockGroup.indexes_to_blocks](#ectypesblockgroupindexes_to_blocks)
    - [ectypes.BlockGroup.get_parity_indexes](#ectypesblockgroupget_parity_indexes)
  - [ectypes.Region](#ectypesregion)
    - [ectypes.Region.add_block](#ectypesregionadd_block)
    - [ectypes.Region.move_down](#ectypesregionmove_down)
    - [ectypes.Region.find_merge](#ectypesregionfind_merge)
    - [ectypes.Region.list_block_ids](#ectypesregionlist_block_ids)
    - [ectypes.Region.replace_block_id](#ectypesregionreplace_block_id)
    - [ectypes.Region.get_block_ids_by_needle_id](#ectypesregionget_block_ids_by_needle_id)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

ectypes

#   Status

The library is considered production ready.

#   Synopsis

```python
from pykit import ectypes

server_id = ectypes.ServerID.local_server_id('idc000')
# idc and 12 chars from primary MAC addr: "idc000c62d8736c728"

serverrec = ectypes.make_serverrec('idc000aabbccddeeff', 'idc000', 'center', {'role1': 1}, "/s2")
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
#   'server_id': 'idc000aabbccddeeff',
#   'next_mount_index': 1,
#   "allocated_drive": {
#       "/s2/dirve/001": {"status": "normal",},
#       "/s2/dirve/002": {"status": "normal",},
#   },
#}
```

#   Description

Some helper function for the server in a ectypes.

#   Exceptions

##  ectypes.BlockNotFoundError

**syntax**:
`ectypes.BlockNotFoundError`

Raise if a block not found in a block group.

##  ectypes.BlockTypeNotSupported

**syntax**:
`ectypes.BlockTypeNotSupported`

Raise if block index do not have corresponding type.

## ectypes.BlockTypeNotSupportReplica

**syntax**:
`ectypes.BlockTypeNotSupportReplica`

Raise if block type do not support replica.

## ectypes.BlockIndexError

**syntax**:
`ectypes.BlockIndexError`

Raise if block index parse or make error.


#   Methods

##  ectypes.make_serverrec

**syntax**:
`ectypes.make_serverrec(server_id, idc, idc_type, roles, allocated_drive_pre, **argkv)`

Make a `dict` (a server record).

-   Collected physical field(pub_ips, inn_ips, hostname, server_id, memory, cpu).

-   User specified field(idc, idc_type, roles(as a dict whose values are 1), other fields if needed).

-   Mounted path(mount path, capacity, fs type).

**arguments**:

-   `server_id`:
    specifies the server id.

-   `idc`:
    The name of a idc in the ectypes. Format: `.l1-name.l2-name...`.

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

##  ectypes.get_serverrec_str

**syntax**:
`ectypes.get_serverrec_str(serverrec)`

Collect some important info(`server_id`, `idc`, `idc_type`, `roles`,
`mountpoints_count`, `allocated_drive_count`) of `serverrec` into a `str`.

**arguments**:

-   `serverrec`:
    The server record return from `ectypes.make_serverrec`.

**return**:
A `str`, like:

```
"server_id: idc12300aabbccddee; idc: .l1; idc_type: zz; roles: {'role1': 1}; mountpoints_count: 3; allocated_drive_count: 0"
```

##  ectypes.validate_idc

**syntax**:
`ectypes.validate_idc(idc)`

Check the name of a idc is valid or not.

**arguments**:

-   `idc`:
    The name of a idc in the ectypes. Format: `.l1-name.l2-name...`.

**return**:
`True` or `False`, means the name is valid or not.

##  ectypes.idc_distance

**syntax**:
`ectypes.idc_distance(idc_a, idc_b)`

Estimate distance between two idc.

**arguments**:

-   `idc_a`:
    First idc name.

-   `idc_b`:
    Second idc name.

**return**:
The distance of them.


#   Classes


##  ectypes.ReplicationConfig

**syntax**:
`ectypes.ReplicationConfig(FixedKeysDict)`

`ReplicationConfig` is a subclass of `FixedKeysDict` thus also a subclass of `dict`.
It provides the same construction function prototype as `dict`.

**keys**:

-   `in_idc`:
    An instance of namedtuple `RSConfig`, which has 2 element: N.O. of data
    and N.O. of parity.

-   `cross_idc`:
    Similar to `in_idc`, it defines cross idc EC parameter.

-   `data_replica`:
    is a number of replicas of block, before encoded with Reed Solomon.
    By default it is 1.
    And it can not be smaller than 1.

**Synopsis**:

```python
print ReplicationConfig(in_idc=[6, 2], cross_idc=[3, 1])
# {"in_idc":[6, 2], "cross_idc":[3, 1], data_replica:1}
```


##  ectypes.IDBase

**syntax**:
`ectypes.IDBase(str)`

A subclass of `str`, it is an *inner* format class for all IDs.

```python
# new
IDBase(xxxID)
IDBase(attr_1_value, attr_2_value, ...)
IDBase(attr_1=value, attr_2=value, ...)
```

### To declare a new ID type:

```
class MyID(IDBase):
    _attrs = (
        ('foo',    0,  1, str),
        ('bar',    1,  2, str),
        ('alias1', 1,  2, str, False),
        ('alias2', 1,  2, str, {'key_attr': False}),
    )

    _str_len = 2

    _tostr_fmt = '{foo}{bar}'
```

`_attr` defines what attribute to extract from input string.
Here we have two attribute `foo` and `bar` and two **alias** attributes `alias1`
and `alias2`.

#### Non key-attribute

To declare an alias attribute, add a fifth field as attribute options:
`{'key_attr': False}` or just a `False` as shortcut.

**Alias attribute does not need to present in constructor**.

With the above definition, MyID can be created in the following ways:

```
MyID('12')
MyID('1', '2')
MyID('1', bar='2')
MyID(foo='1', bar='2')
```

#### Self attribute

To declare a **self** attribute, which reference the instance itself, use opt:
`{'self': True}` or `'self'` as a shortcut.

```
class MyID(IDBase):
    _attrs = (
        ('foo',    0,  1, str),
        ('me',     None,  None, None, 'self'),
    _str_len = 1

i = MyID('a')
print i is i.me    # True
print i is i.me.me # True
```


#### Embedded attribute

To embed sub-attributes, use opt:
`{'embed': True}` or `'embed'` as shortcut:

```
class SubID1(IDBase):
    _attrs = (
        ('one',  0,  1, lambda x: 1),
    )
    _str_len = 1


class MyID(IDBase):
    _attrs = (
        ('foo',  0,  1, str),
        ('sub',  1,  2, SubID1, 'embed'),
    )
    _str_len = 2

i = MyID('ab')
print i.sub.one     # 1
print i.one         # 1
```


##  ectypes.IDCID

**syntax**:
`ectypes.IDCID(idc_id)`

`IDCID` is a subclass of `str` representing an idc.

**arguments**:

-   `idc_id`: a 6-char string.


##  ectypes.ServerID

**syntax**:
`ectypes.ServerID(str)`

**syntax**:
`ectypes.ServerID(idc_id, mac_addr)`

**arguments**:

-   `idc_id`:
    an `IDCID` instance

-   `mac_addr`:
    a 12-hex-char string.


##  ectypes.local_server_id

**syntax**:
`ectypes.local_server_id(idc_id)`

**arguments**:

-   `idc_id`: a string or an `IDCID` instance.

**return**:
a server id, format: 6 char idc and 12 chars from primary MAC
addr(e.g.: "idc123" "c62d8736c728").

```python
from pykit import ectypes

print ectypes.ServerID.local_server_id('idc123')
# out: idc12300163e0630f7
```


##  ectypes.DriveID

**syntax**:
`ectypes.DriveID(server_id, mount_point_index)`

A subclass of `IDBase`. Make a drive id, format: 16 chars
`<server_id>0<mount_point_index><port>`

**arguments**:

-   `server_id`:
    A string, Format: 18 chars of idc and primary MAC addr.

-   `mount_point_index`:
    It is a 3-digit mount path, `001` for `/drives/001`.


```python
from pykit import ectypes

print ectypes.DriveID('idc000' 'aabbccddeeff', 10)
# out: aabbccddeeff0010
```

`DriveID` embeds `ServerID` attributes.


##  ectypes.BlockID

**syntax**:
`BlockID(type, block_group_id, block_index, drive_id, block_id_seq)`

A subclass of `IDBase`. Generate block id.

```python
block_id = 'd0g0006300000001230101idc000c62d8736c72800020000000001'

bid = ectypes.BlockID(block_id)
print bid.type            # d
print bid.block_group_id  # g000630000000123
print bid.block_index     # 0101
print bid.drive_id        # idc000c62d8736c7280002
print bid.block_id_seq    # 1

# test __str__()
print bid                 # d0g0006300000001230101idc000c62d8736c72800020000000001
```

`BlockID` embeds `DriveID` attributes.


### block id

`block_id`: identifies a single data or parity block.

A block is a single file on disk that contains multiple user-file.

Format: 54 chars

```
(d0|d1|d2|dp|x0|xp)<block_group_id><block_index><drive_id><block_id_seq>
2                  16              4            22        10
```

Example: `d g000630000000123 0101 idc000 c62d8736c7280002 0000000001`(without
space)


-   `type`:

    -   `d0`(data) for a `data_block`.

    -   `d1`, `d2`(the 1st and 2nd copy of data) for a `data_block`.

        If `config.ec.in_idc` config is `[4, 2]`,

        Block index of the first copy of data block `i` with `type=d1` is:
        `idc_index` `in_idc[0] + in_idc[1] + i`.

        Block index of the second copy of data block `i` with `type=d2` is:
        `idc_index` `in_idc[0] + in_idc[1] + in_idc[0] + i`.

        E.g.

        and lock `0002` has 2 copies, block indexes for these two copies are:
        `0010` and `0012`

    -   `dp`(parity of data) a in-IDC `parity_block`.

    -   `x0`(xor-parity) for a cross-IDC xor based `parity_block`.

    -   `xp`(parity of xor-parity).


    `type` layout for a block group with copies:

    ```
    data          parity  1st-copy      2nd-copy
    ----          ------  --------      --------
    d0 d0 d0 d0   dp dp   d1 d1 d1 d1   d2 d2 d2 d2
    d0 d0 d0 d0   dp dp   d1 d1 d1 d1   d2 d2 d2 d2

    x0 x0 x0 x0   xp xp
    ```

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

-   `block_id_seq`:
    is a block group wise monotonic incremental id.
    To ensure that any two blocks have different `block_id`.


##  ectypes.BlockIndex

**syntax**:
`BlockIndex(i, j)`

A subclass of `IDBase`. Make block index.

```python
block_index = '1234'

bi = ectypes.BlockIndex(block_index)
print bi.i      # 12
print bi.j      # 34

print bi        # 1234
```


##  ectypes.BlockDesc

**syntax**:
`ectypes.BlockDesc(FixedKeysDict)`

Initialize block use a dict.

Block keys include:

-   `size`: int, in byte; on-disk block file size, default is 0.
-   `range`: rangeset.Range(); block range, not active range in region. Default is rangeset.Range(None, None).
-   `block_id`: BlockID(). Default is None.
-   `is_del`: 0 or 1. Default is 0.


##  ectypes.BlockGroupID

**syntax**:
`BlockGroupID(block_size, seq)`

A subclass of `IDBase`. Generate block group id.

```python
block_group_id = 'g000640000000123'

bgid = ectypes.BlockGroupID(block_group_id)
print bgid.block_size  # 64
print bgid.seq         # 123

# test __str__()
print bgid             # g000640000000123
```

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

    A `seq` is unique in a ectypes.

Example: `g 00064 0000000123`(without space).


## ectypes.BlockGroup

BlockGroup meta operations.

**syntax**:
`ectypes.BlockGroup(FixedKeysDict)`

A `BlockGroup` is subclass of dict thus it shares the same construction API with
`dict`.

When initializing, the following 3 items must be specified:

- `block_group_id` is a `BlockGroupID` instance or string.
- `idcs` is a list of idc name in string.
- `config` is a `ReplicationConfig` instance or plain `dict`

### block index

`block_index`: specifies the block position in a `block_group`.

It is a 4 digit decimal `number`:

-   The first 2 digits is the IDC index.

-   The latter 2 digits is the position in a IDC.

Both these 2 parts starts from 00.

E.g.: `block_index` of the 1st block in the first IDC is: `0000`.
`block_index` of the 2nd block in the 3rd IDC is: `0201`.

### ectypes.BlockGroup.get_block

**syntax**:
`ectypes.BlockGroup.get_block(block_index, raise_error=False)`

**arguments**:

-   `block_index`:
    a string or `BlockIndex`.

-   `raise_error`:
    raise `BlockNotFoundError` if `raise_error` is `True` and block not found.
    Default is `False`

**return**:
`(block_index, block)`

### ectypes.BlockGroup.get_free_block_indexes

**syntax**:
`ectypes.BlockGroup.get_free_block_indexes(block_type=None, get_all=False)`

**arguments**:

-   `block_type`:
    Type of the block.

-   `get_all`:
    specifies if to set no free block idc as a key in the result `dict`.
    A `bool`, by default it is `False`.

**return**
A dict that key is idc and value is a list of `block_index`.
If `get_all` is `True`, value of no free block idc is `[]`.

### ectypes.BlockGroup.mark_delete_block

**syntax**:
`ectypes.BlockGroup.mark_delete_block(block_index)`

Mark a block to be `deleted` by setting its `is_del` field to `1`.

-   `block_index`:
    a string or `BlockIndex`.

**return**:
Nothing.
Will raise `BlockNotFoundError` if target block not found.

### ectypes.BlockGroup.delete_block

**syntax**:
`ectypes.BlockGroup.delete_block(block_index)`

Delete a block if it is in this group.
Do nothing if the specified block index not found.

-   `block_index`:
    a string or `BlockIndex`.

**return**:
Nothing.
Will raise `BlockNotFoundError` if target block not found.

### ectypes.BlockGroup.add_block

**syntax**:
`ectypes.BlockGroup.add_block(new_block, replace=False)`

-   `new_block`:
    is a `BlockDesc` or plain `dict` to replace.

-   `replace`:
    whether allowing to add a block at index where there is already a block.

    If it is `False` and there is a block, it raises `BlockExists`.

**return**:
a `BlockDesc` instance of the replace block.
It is `None` if there is no block at the index.

### ectypes.BlockGroup.get_block_type

**syntax**:
`ectypes.BlockGroup.get_block_type(block_index)`

-   `block_index`:
    a string or `BlockIndex`.

**return**:
block type.
Will raise `BlockTypeNotSupported` if block index do not have corresponding type.

### ectypes.BlockGroup.get_block_idc

**syntax**:
`ectypes.BlockGroup.get_block_idc(block_index=None)`

-   `block_index`:
    a string or `BlockIndex`.

**return**:
The idc in string of the block.

### ectypes.BlockGroup.get_replica_indexes

**syntax**:
`ectypes.BlockGroup.get_replica_indexes(block_index, include_me=True)`

-   `block_index`:
    a string or `BlockIndex`.

-   `include_me`:
    whether including `block_index` itself in return value

**return**:
List of data replica block index.
Will raise `BlockTypeNotSupportReplica` if block type do not support replica.

### ectypes.BlockGroup.classify_blocks

**syntax**:
`ectypes.BlockGroup.classify_blocks(idc_index, only_primary=True)`

-   `idc_index`:
    type is number, the index of idc in block_group idcs list.

-   `only_primary`:
    whether including type d1, d2 replicas in returned replica list.

**return**:
dict of blocks include ec, replica, mark_del.

### ectypes.BlockGroup.indexes_to_blocks

**syntax**:
`ectypes.BlockGroup.indexes_to_blocks(indexes)`

-   `indexes`:
    list of block indexes.

**return**:
List of block instances, if index has no block, it will be None in list.

### ectypes.BlockGroup.get_parity_indexes

**syntax**:
`ectypes.BlockGroup.get_parity_indexes(idc_index)`

-   `idc_index`:
    type is number, the index of idc in block_group idcs list.

**return**:
List of parity block index.

**syntax**:
`ectypes.BlockGroup.get_parities(idc_index)`

-   `idc_index`:
    type is number, the index of idc in block_group idcs list.

**return**:
List of parity block instance, only existed parity in the return list.

## ectypes.Region

**syntax**:
`ectypes.Region(FixedKeysDict)`

Region related operations.

### ectypes.Region.add_block

**syntax**:
`ectypes.Region.add_block(active_range, block, level=None)`

Add a block to a region level.

**arguments**:

-   `active_range`:
    is the active boundary of the `block` in this region. A list: `[left, right]`.

-   `block`:
    is the information of the block to add to this region. A dict:
    ```
    {
        "block_range": ["<block_left>", "<block_right>"],
        "block_id": "<block_id>",
        "size": 1234,
    }
    ```

-   `level`:
    is the region level to add `block`.
    If `level` is not specified or `None`, add block to the `max(level)+1` level.

**return**:
Nothing.

If `level` is specified but not in this region levels boundry(`0<=level<=max(level)+1`),
`LevelOutOfBound` is raised.

### ectypes.Region.move_down

**syntax**:
`ectypes.Region.move_down()`

A move includes blocks from two different, adjacent levels.
If block A overlaps with no lower level blocks, move it downward.
`move_down` moves all movable blocks in this region.

**arguments**:
Nothing

**return**:

A list of `(source_level, target_level, block)`.
This list of 3-tuple records all movable blocks which should move from
`source_level` to `target_level`.

### ectypes.Region.find_merge

**syntax**:
`ectypes.Region.find_merge()`

A merge includes blocks from two different, adjacent level.
If block A overlaps lower level blocks set s = {X, Y...}. and size(A) >= size(s)/4, merge them.
`find_merge` find one block and its overlapped blocks that can merge and return.

**arguments**:
Nothing

**return**:

-   `src_level`
    level of `src_block` that can merge downward.

-   `src_block`
    the block that can merge downward.

-   `overlapped_blocks`
    blocks in lower level that have overlap with `src_block`.

If no blocks can merge, return None.

### ectypes.Region.list_block_ids

**syntax**:
`ectypes.Region.list_block_ids(start_block_id=None)`

list all block ids in this region alphabetical from `start_block_id`.

**arguments**:

-   `start_block_id`
    used as the starting of block id list.
    If it not exists in block id list, the starting is the first one bigger than it.

**return**:
a block id list.

### ectypes.Region.replace_block_id

**syntax**:
`ectypes.Region.replace_block_id(block_id, new_block_id)`

replace block id from `block_id` to `new_block_id`.

**arguments**:

-   `block_id`
    the block id to be replaced.

-   `new_block_id`
    the block id should be replaced to.

**return**:
Nothing.
If `block_id` is not found in region levels, raise `BlockNotInRegion`.

### ectypes.Region.get_block_ids_by_needle_id

**syntax**:
`ectypes.Region.get_block_ids_by_needle_id(needle_id)`

Returns the block_id of all blocks that may have 'needle_id'

**arguments**:

-   `needle_id`
    the needle id to be searched 

**return**:
Return a list of `block_id`, the higher level blocks are in front.
If `needle_id` is not in this region, return an empty list.

#   Author

Baohai Liu(刘保海) <baohai.liu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Baohai Liu(刘保海) <baohai.liu@baishancloud.com>
