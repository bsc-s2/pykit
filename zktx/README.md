<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Accessor classes](#accessor-classes)
  - [zktx.KVAccessor](#zktxkvaccessor)
  - [zktx.ValueAccessor](#zktxvalueaccessor)
  - [zktx.ZKKeyValue](#zktxzkkeyvalue)
  - [zktx.ZKValue](#zktxzkvalue)
- [Storage classes](#storage-classes)
  - [zktx.Storage](#zktxstorage)
    - [Storage attributes](#storage-attributes)
    - [Storage methods](#storage-methods)
      - [Storage.try_lock_key](#storagetry_lock_key)
      - [Storage.try_release_key](#storagetry_release_key)
    - [Storage helper methods](#storage-helper-methods)
  - [zktx.StorageHelper](#zktxstoragehelper)
    - [StorageHelper.get_latest](#storagehelperget_latest)
    - [StorageHelper.apply_record](#storagehelperapply_record)
    - [StorageHelper.add_to_txidset](#storagehelperadd_to_txidset)
  - [zktx.ZKStorage](#zktxzkstorage)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


#   Name

zktx

#   Status

This library is considered production ready.

#   Description

Transaction implementation on Zookeeper.

#   Accessor classes

##  zktx.KVAccessor

**syntax**:
`zktx.KVAccessor()`

An abstract class that defines an underlaying storage access API.
An implementation of `KVAccessor` must provides with 4 API:

```python
def create(self, key, value):
def delete(self, key, version=None):
def set(self, key, value, version=None):
def get(self, key):
```

They are similar to zk APIs, except that `version` does not have to be a version
number.
It could be any data type the implementation could understand.


##  zktx.ValueAccessor

Same as `KVAccessor` except the API it defines does not require the argument
`key`.
It is used to access a single node:

```python
def create(self, value):
def delete(self, version=None):
def set(self, value, version=None):
def get(self):
```

##  zktx.ZKKeyValue

**syntax**:
`zktx.ZKKeyValue(zkclient, get_path=None, load=None, dump=None, nonode_callback=None)`

An zk based `KVAccessor` implementation.
It provides 4 API `get`, `set`, `create` and `delete` to operate a zk-node.

**arguments**:

-   `zkclient`:
    is a `kazoo.client.Client` instance.

-   `get_path`:
    is a callback to convert `key`(the first argument for the 4 methods.) to a zk-node path.

    By default it is `None`: to use `key` directly as path.

-   `load`:
    is an optional callback to convert value for `get`.
    E.g.

    ```python
    def foo_load(val):
        return '(%s)' % val
    ```

-   `dump`:
    is an optional callback to convert value for `set` and `create`.
    E.g.

    ```python
    def foo_dump(val):
        return val.strip('()')
    ```

-   `nonode_callback`:
    is an optional callback to make a tuple of `value, version` when `get`
    encountered a `NoNodeError` error.

    If it is `None`, `NoNodeError` is raised.

    E.g.:

    ```python
    def nonode_callback():
        return '', -1
    ```


##  zktx.ZKValue

**syntax**:
`zktx.ZKValue(zkclient, get_path=None, load=None, dump=None, nonode_callback=None)`

Same as `ZKKeyValue` except that `get_path` does not receive an argument `key`,
Because a single value accessor operates on only one zk-node.


#   Storage classes


##  zktx.Storage

**syntax**:
`zktx.Storage()`

This is an abstract class that defines what a storage layer should provides for
a transaction engine.

Our TX engine is able to run on any storage that implements `Storage`.


### Storage attributes

To support a transaction to run,
a class that implements `Storage` must provides 3 accessors(`KVAccessor` and `ValueAccessor`):

-   `record`:
    is a `KVAccessor` to get or set a user-data record.

    A record value is a `dict` map of `txid` to value:

    ```python
    {
        <txid>: <value>
        <txid>: <value>
        ...
    }
    ```

-   `journal`:
    is a `KVAccessor` to get or set a tx journal.

    Journal value is not define on storage layer.
    A TX engine defines the value format itself.

-   `txidset`:
    is a `ValueAccessor`.
    It is a single value accessor to get or set transaction id set.

    Value of `txidset` is a `dict` of 3 `RangeSet`(see module `rangeset`):

    ```python
    {
        "COMMITTED": RangeSet(),
        "ABORTED": RangeSet(),
        "PURGED": RangeSet(),
    }
    ```

    -   `COMMITTED` contains committed txid.

    -   `ABORTED` contains aborted txid.
        Abort means a tx is killed before writing a `journal`.

    -   `PURGED` contains txid whose journal has been removed.

    > `COMMITTED`, `ABORTED` and `PURGED` has no intersection.


### Storage methods

An implementation of `Storage` must implement 2 locking methods:

####  Storage.try_lock_key

**syntax**:
`Storage.try_lock_key(txid, key)`

It is defined as `def try_lock_key(self, txid, key)`.

It tries to lock a `key` for a `txid`: Same `txid` can lock a `key` more than once.

This function should never block and should return at once.

> Because our TX engine need to detect and resolve deadlock, thus locking should
> be non-blocking.

It should return a 3 element `tuple`:

-   A `bool` indicates if locking succeeds.

-   A `txid` indicates current lock holder.
    If locking succeeded, it is the passed in `txid`

-   A 3rd value indicates lock stat(not used yet).


####  Storage.try_release_key

**syntax**:
`Storage.try_release_key(txid, key)`

It should release the lock identified by `key`, if and only if the lock is held
by `txid`

> This way only the lock holder could release the lock, without the need to
> know if it has already acquired the lock.
> This makes the recovery of a tx processor very easy:
> A recovered process only need to know the `txid` but not the locking
> informations.

It should returns 3 element `tuple`:

-   A `bool` indicates if the lock is previously locked by any one.

-   A `txid` indicates current lock holder.
    If no one has been locking it, it is the passed in `txid`

-   A 3rd value indicates lock stat(not used yet).

### Storage helper methods

There are also 3 methods an TX engine requires, which are already provided
by `StorageHelper`.

An implementation class could just extend `StorageHelper` to make these 3 methods available.
See `StorageHelper`.


##  zktx.StorageHelper

**syntax**:
`class StorageHelper(object)`

It provides 3 methods those a TX engine relies on.
Since underlying accessors has already been provided, these 3 methods are
implementation unrelated.


###  StorageHelper.get_latest

**syntax**:
`StorageHelper.get_latest(key)`

It returns the latest update(the update with the greatest txid) of a record identified by `key`.

It requires 1 accessor method: `self.record.get(key)`.

**arguments**:

-   `key`:
    specifies the `key` of the record.

**return**:
a dict in form of `{<txid>: <value>}` and an implementation defined version.


###  StorageHelper.apply_record

**syntax**:
`StorageHelper.apply_record(txid, key, value)`

This method applies an update to underlying storage.

It requires 2 accessor methods: `self.record.get(key)`
and `self.record.set(key, value, version=None)`.

**arguments**:

-   `txid`:
    transaction id.

-   `key`:
    record key.

-   `value`:
    record value.

**return**:
a `bool` indicates if change has been made to underlying storage.
Normal it is `False` if a higher txid has already been applied.


###  StorageHelper.add_to_txidset

**syntax**:
`StorageHelper.add_to_txidset(status, txid)`

It records a txid as one of the possible status: COMMITTED, ABORTED or PURGED.

It requires 2 accessor methods: `self.txidset.get()`
and `self.txidset.set(value, version=None)`.

**arguments**:

-   `status`:
    specifies tx status

-   `txid`:
    transaction id.

**return**:
Nothing

##  zktx.ZKStorage

**syntax**:
`zktx.ZKStorage(zkclient)`

`ZKStorage` is an implementation of `Storage`, whose accessors and locks a re
stored in zk.

**arguments**:

-   `zkclient`:
    must be a `zkutil.KazooClientExt` instance.



#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
