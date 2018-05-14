
#   Name

zktx

#   Status

This library is considered production ready.

#   Description

Transaction implementation on Zookeeper.

#   Classes

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


##  zktx.TXStorage

**syntax**:
`zktx.TXStorage()`

This is an abstract class that defines what a storage layer should provides for
a transaction engine.

Our TX engine is able to run on any storage that implements `TXStorage`.


### TXStorage attributes

To support a transaction to run,
a class that implements `TXStorage` must provides 3 accessors(`KVAccessor` and `ValueAccessor`):

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


### TXStorage methods

An implementation of `TXStorage` must implement 2 locking methods:

####  TXStorage.try_lock_key

**syntax**:
`TXStorage.try_lock_key(txid, key)`

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


####  TXStorage.try_release_key

**syntax**:
`TXStorage.try_release_key(txid, key)`

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

### TXStorage helper methods

There are also two 3 methods an TX engine requires, which are already provided
by `TXStorageHelper`.

An implementation class could just extend `TXStorageHelper` to make these 3 methods available.
See `TXStorageHelper`.


##  zktx.TXStorageHelper

**syntax**:
`class TXStorageHelper(object)`

It provides 3 methods those a TX engine relies on.
Since underlying accessors has already been provided, these 3 methods are
implementation unrelated.


###  TXStorageHelper.get_latest

**syntax**:
`TXStorageHelper.get_latest(key)`

It returns the latest update(the update with the greatest txid) of a record identified by `key`.

It requires 1 accessor method: `self.record.get(key)`.

**arguments**:

-   `key`:
    specifies the `key` of the record.

**return**:
a dict in form of `{"txid": ..., "value": ...}` and a implementation defined version.


###  TXStorageHelper.apply_record

**syntax**:
`TXStorageHelper.apply_record(txid, key, value)`

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
Normal it is `False` if a higher txid has already applied.


###  TXStorageHelper.add_to_txidset

**syntax**:
`TXStorageHelper.add_to_txidset(status, txid)`

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


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
