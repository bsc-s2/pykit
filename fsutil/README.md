<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Synopsis](#synopsis)
- [Exceptions](#exceptions)
  - [NotMountPoint](#notmountpoint)
- [Methods](#methods)
  - [fsutil.assert_mountpoint](#fsutilassert_mountpoint)
  - [fsutil.get_device](#fsutilget_device)
  - [fsutil.get_disk_partitions](#fsutilget_disk_partitions)
  - [fsutil.get_mountpoint](#fsutilget_mountpoint)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

fsutil

#   Status

This library is considered production ready.

#   Description

File-system Utilities.


# Synopsis

```python
fsutil.get_mountpoint('/bin')
# '/'

fsutil.get_device('/bin')
# '/dev/sdb1'

fsutil.get_disk_partitions()
# {
#  '/': {'device': '/dev/disk1',
#        'fstype': 'hfs',
#        'mountpoint': '/',
#        'opts': 'rw,local,rootfs,dovolfs,journaled,multilabel'},
#  '/dev': {'device': 'devfs',
#           'fstype': 'devfs',
#           'mountpoint': '/dev',
#           'opts': 'rw,local,dontbrowse,multilabel'},
#  ...
# }
```

# Exceptions

## NotMountPoint

Raises when trying to use an invalid mount point path.


# Methods

##  fsutil.assert_mountpoint

**syntax**:
`fsutil.assert_mountpoint(path)`

Ensure that `path` must be a **mount point**.
Or an error `NotMountPoint` is emitted.

**arguments**:

-   `path`:
    is a path that does have to be an existent file path.

**return**:
Nothing


##  fsutil.get_device

**syntax**:
`fsutil.get_device(path)`

Get the device path(`/dev/sdb` etc) where `path` resides on.

**arguments**:

-   `path`:
    is a path that does have to be an existent file path.

**return**:
device path like `"/dev/sdb"` in string.


##  fsutil.get_disk_partitions

**syntax**:
`fsutil.get_disk_partitions()`

Find and return all mounted path and its mount point information in a
dictionary.

All mount points including non-disk path are also returned.

**return**:
an dictionary indexed by mount point path:

```python
{
 '/': {'device': '/dev/disk1',
       'fstype': 'hfs',
       'mountpoint': '/',
       'opts': 'rw,local,rootfs,dovolfs,journaled,multilabel'},
 '/dev': {'device': 'devfs',
          'fstype': 'devfs',
          'mountpoint': '/dev',
          'opts': 'rw,local,dontbrowse,multilabel'},
 '/home': {'device': 'map auto_home',
           'fstype': 'autofs',
           'mountpoint': '/home',
           'opts': 'rw,dontbrowse,automounted,multilabel'},
 '/net': {'device': 'map -hosts',
          'fstype': 'autofs',
          'mountpoint': '/net',
          'opts': 'rw,nosuid,dontbrowse,automounted,multilabel'}
}
```


##  fsutil.get_mountpoint

**syntax**:
`fsutil.get_mountpoint(path)`

Return the mount point where this `path` resides on.
All symbolic links are resolved when looking up for mount point.

**arguments**:

-   `path`:
    is a path that does have to be an existent file path.

**return**:
the mount point path(one of output of command `mount` on linux)


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
