<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Synopsis](#synopsis)
  - [Use with statement](#use-with-statement)
  - [Use transaction function](#use-transaction-function)
- [Exceptions](#exceptions)
  - [TXError](#txerror)
  - [Aborted](#aborted)
  - [RetriableError](#retriableerror)
    - [`HigherTXApplied(Aborted, RetriableError)`](#highertxappliedaborted-retriableerror)
    - [`Deadlock(Aborted, RetriableError)`](#deadlockaborted-retriableerror)
  - [UserAborted](#useraborted)
  - [TXTimeout](#txtimeout)
  - [ConnectionLoss](#connectionloss)
- [Accessor classes](#accessor-classes)
  - [zktx.KeyValue](#zktxkeyvalue)
  - [zktx.Value](#zktxvalue)
  - [zktx.ZKKeyValue](#zktxzkkeyvalue)
  - [zktx.ZKValue](#zktxzkvalue)
  - [zktx.RedisKeyValue](#zktxrediskeyvalue)
  - [zktx.RedisValue](#zktxredisvalue)
- [Storage classes](#storage-classes)
  - [zktx.Storage](#zktxstorage)
    - [Storage attributes](#storage-attributes)
    - [Storage methods](#storage-methods)
      - [Storage.acquire_key_loop](#storageacquire_key_loop)
      - [Storage.try_release_key](#storagetry_release_key)
    - [Storage helper methods](#storage-helper-methods)
  - [zktx.StorageHelper](#zktxstoragehelper)
    - [StorageHelper.apply_record](#storagehelperapply_record)
    - [StorageHelper.add_to_txidset](#storagehelperadd_to_txidset)
  - [zktx.ZKStorage](#zktxzkstorage)
  - [zktx.RedisStorage](#zktxredisstorage)
    - [zktx.RedisStorage.apply_jour](#zktxredisstorageapply_jour)
    - [zktx.RedisStorage.apply_record](#zktxredisstorageapply_record)
    - [zktx.RedisStorage.add_to_txidset](#zktxredisstorageadd_to_txidset)
    - [zktx.RedisStorage.set_txidset](#zktxredisstorageset_txidset)
- [Transaction classes](#transaction-classes)
  - [zktx.TXRecord](#zktxtxrecord)
  - [zktx.ZKTransaction](#zktxzktransaction)
    - [ZKTransaction.lock_get](#zktransactionlock_get)
    - [ZKTransaction.set](#zktransactionset)
    - [ZKTransaction.commit](#zktransactioncommit)
    - [ZKTransaction.abort](#zktransactionabort)
  - [zktx.run_tx](#zktxrun_tx)
- [Slave class](#slave-class)
  - [zktx.Slave](#zktxslave)
    - [zktx.Slave.apply](#zktxslaveapply)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


#   Name

zktx

#   Status

This library is considered production ready.

#   Description

Transaction implementation on Zookeeper.

Following chapters describes API of this module.
To see more about transaction design, See [transaction](transaction.md)


#   Synopsis

## Use with statement

```python
while True:
    try:
        with ZKTransaction('127.0.0.1:2181', timeout=3) as tx:

            foo = tx.lock_get('foo')
            print foo.k    # "foo"
            print foo.txid # 1 or other integer

            foo.v = 1
            tx.set(foo)

            bar = tx.lock_get('bar')
            if bar.v == 1:
                bar.v = 2
                tx.set(bar)
                tx.commit()
            else:
                tx.abort()

    except (Deadlock, HigherTXApplied):
        continue
    except (TXTimeout, ConnectionLoss) as e:
        print repr(e)
        break
```

## Use transaction function

```python
def tx_work(tx, val):
    foo = tx.lock_get('foo')
    foo.v = val
    tx.set(foo)
    tx.commit()

try:
    # run_tx() handles RetriableError internally.
    zktx.run_tx('127.0.0.1:2181', tx_work, args=(100, ))
except (TXTimeout, ConnectionLoss) as e:
    print repr(e)
```


#   Exceptions

##  TXError

Super class of all zktx exceptions


##  Aborted

`Aborted` is the super class of all errors that abort a tx.
It should **NOT** be used directly.


##  RetriableError

It is a super class of all retrieable errors.

Sub classes are:

### `HigherTXApplied(Aborted, RetriableError)`

It is raised if a higher txid than current tx has been seen when reading a `record`.

Because tx must be applied in order, if a higher txid is seen user should
abort current tx and retry(with a new higher txid).

E.g.:

```
| tx-1                       | tx-2                        |
| :---                       | :---                        |
| created                    | created                     |
|                            | lock('foo') OK              |
| lock('foo') blocked        |                             |
|                            | get('foo') latest-txid = -1 |
|                            | set('foo', 10)              |
|                            | commit()                    |
| lock('foo') OK             |                             |
| get('foo') latest-txid = 2 |                             |
| raise HigherTXApplied()    |                             |
```

### `Deadlock(Aborted, RetriableError)`

It is raised if a **potential** dead lock is detected:
If a higher txid tries to lock a key which is held by a smaller txid.


## UserAborted

It is raised if user calls `tx.abort()`.

**A program does not need to catch this error**.
It is used only for internal communication.


## TXTimeout

It is raised if tx fails to commit before specified running time(`timeout`).

**A program should always catch this error**.


##  ConnectionLoss

It is raised if tx loses connection to zk.

**A program should always catch this error**.


#   Accessor classes

##  zktx.KeyValue

**syntax**:
`zktx.KeyValue()`

An abstract class that defines an underlying storage access API.
An implementation of `KeyValue` must provides with 4 API:

```python
def create(self, key, value):
def delete(self, key, version=None):
def set(self, key, value, version=None):
def get(self, key):
```

They are similar to zk APIs, except that `version` does not have to be a version
number.
It could be any data type the implementation could understand.


##  zktx.Value

Same as `KeyValue` except the API it defines does not require the argument
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

An zk based `KeyValue` implementation.
It provides 4 API `get`, `set`, `create` and `delete` to operate a zk-node.

Note: If `zkclient._zkconf` has acl, znode's acl would set automatically when created.

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

Note: If `zkclient._zkconf` has acl, znode's acl would set automatically when created.

##  zktx.RedisKeyValue

**syntax**:
`zktx.RedisKeyValue(redis_cli, get_path=None, load=None)`

It provides 4 API `get`, `set`, `hget` and `hset` to operate a redis-node.

**arguments**:

-   `redis_cli`:
    is a `redis.StrictRedis` instance.

-   `get_path`:
    is a callback to convert `key`(the first argument for the 4 methods.) to a redis-node path.

    By default it is `None`: to use `key` directly as path.

-   `load`:
    is an optional callback to convert value for `get`.
    E.g.

    ```python
    def foo_load(val):
        return '(%s)' % val
    ```


##  zktx.RedisValue

**syntax**:
`zktx.RedisValue(redis_cli, get_path=None, load=None)`

Same as `RedisKeyValue` except that `get_path` does not receive an argument `key`,
Because a single value accessor operates on only one redis-node.


#   Storage classes


##  zktx.Storage

**syntax**:
`zktx.Storage()`

This is an abstract class that defines what a storage layer should provides for
a transaction engine.

Our TX engine is able to run on any storage that implements `Storage`.


### Storage attributes

To support a transaction to run,
a class that implements `Storage` must provides 3 accessors(`KeyValue` and `Value`):

-   `record`:
    is a `KeyValue` to get or set a user-data record.

    A record value is a `list` of `[txid, value]`:

    ```python
    [[1, "foo"],
     [2, "bar"],
    ]
    ```

-   `journal`:
    is a `KeyValue` to get or set a tx journal.

    Journal value is not define on storage layer.
    A TX engine defines the value format itself.

-   `txidset`:
    is a `Value`.
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

####  Storage.acquire_key_loop

**syntax**:
`Storage.acquire_key_loop(txid, key)`

It is defined as `def acquire_key_loop(self, txid, key)`.

It tries to lock a `key` for a `txid`: Same `txid` can lock a `key` more than once.

It is a wrapper of `zkutil.ZKLock.acquire_loop`.


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


##  zktx.RedisStorage

**syntax**:
`zktx.RedisStorage(redis_cli, txidset_path)`

It provide some functions to save data with redis.

**arguments**:

-   `redis_cli`:
    is a `redis.StrictRedis` instance.

-   `txidset_path`:
    the path of txidset in redis.


### zktx.RedisStorage.apply_jour

**syntax**:
`zktx.RedisStorage.apply_jour(jour)`

Set journal to redis.

**arguments**:

-   `jour`:
    a `dict`, the values that will be saved.

**return**:
nothing


### zktx.RedisStorage.apply_record

**syntax**:
`zktx.RedisStorage.apply_record(key, val)`:

Set `val` to redis with `key`.

**arguments**:

-   `key`:
    a `str`, format `meta/<hashname>/<hashkey>`.

-   `val`:
    specifies the value to redis.

**return**:
nothing


### zktx.RedisStorage.add_to_txidset

**syntax**:
`zktx.RedisStorage.add_to_txidset(status, txid)`:

It records a txid as one of the possible status: COMMITTED, ABORTED or PURGED.

**arguments**:

-   `status`:
    specifies tx status.

-   `txid`:
    transaction id.

**return**:
nothing


### zktx.RedisStorage.set_txidset

**syntax**:
`zktx.RedisStorage.set_txidset(status, txidset)`:

It records a txidset as one of the possible status: COMMITTED, ABORTED or PURGED.

**arguments**:

-   `status`:
    specifies tx status.

-   `txid`:
    transaction id set.

**return**:
nothing


#  Transaction classes


##  zktx.TXRecord

**syntax**:
`zktx.TXRecord(k, v, txid)`

It is a simple wrapper class of key, value and the `txid` in which the value is
updated.

`ZKTransaction.lock_get()` returns a `TXRecord` instance.


##  zktx.ZKTransaction

**syntax**:
`zktx.ZKTransaction(zk, timeout=None)`

It is a transaction engine.

**arguments**:

-   `zk`:
    is the connection argument, which can be:

    -   Comma separated host list, such as
        `"127.0.0.1:2181,127.0.0.2:2181"`.

    -   A `zkutil.ZKConf` instance specifying connection argument with other
        config.

    -   A plain `dict` to create a `zkutil.ZKConf` instance.

-   `timeout`:
    specifies the total time for tx to run.

    If `timeout` exceeded, a `TXTimeout` error will be raised.


###  ZKTransaction.lock_get

**syntax**:
`ZKTransaction.lock_get(key)`

Lock a record identified by `key` and retrieve the record and return.

To guarantee atomic update to multiple records, a record must be locked before
reading it.
Even if a tx does not need to write to this record.

`lock_get()` on a same key more than one time is OK.
But it always returns a copy of the first returned `TXRecord`.

**arguments**:

-   `key`:
    is the record key in string.

**return**:
a `TXRecord` instance.


###  ZKTransaction.set

**syntax**:
`ZKTransaction.set(rec)`

Tell the tx instance the `rec` should be update when committing.

A record that the tx not `set()` it will not be written when committing.

Calling `set(rec)` twice with a same record is OK and has no side effect.


**arguments**:

-   `rec`:
    is a `TXRecord` instance returned from `ZKTransaction.lock_get()`

**return**:
nothing.


###  ZKTransaction.commit

**syntax**:
`ZKTransaction.commit()`

Write all update to zk.

It might raise errors: `TXTimeout`, `ConnectionLoss`.

**return**:
nothing.


###  ZKTransaction.abort

**syntax**:
`ZKTransaction.abort()`

Cancel a tx and write nothing to zk.

**return**:
nothing.


##  zktx.run_tx

**syntax**:
`zktx.run_tx(zk, func, timeout=None, args=(), kwargs=None)`

Start a tx and run it.
Tx operations are define by a callable: `func`.

`func` accepts at least one argument `tx`.
More arguments specified by `args` and `kwargs` are also passed to `func`.

If a `RetriableError` is raised during tx running, `run()` will catch it
and create a new tx and call `func` again,
until tx commits or `timeout` exceeds.

When using `run()`, `timeout` is the total time for all tx `run()` created.

**Synopsis**:

```python
def tx_work(tx, val):
    foo = tx.lock_get('foo')
    foo.v = val
    tx.set(foo)
    tx.commit()

try:
    zktx.run_tx('127.0.0.1:2181', tx_work, timeout=3, args=(100, ))
except (TXTimeout, ConnectionLoss) as e:
    print repr(e)
```

**arguments**:

-   `zk`:
    is same as the `zk` in `ZKTransaction`.

-   `func`:
    a callable object that defines tx operations.

-   `timeout`:
    specifies the total time for tx to run.

    If `timeout` exceeded, a `TXTimeout` error will be raised.

-   `args`:
    specifies additional positioned arguments.
    Such as `args=(1, )`.

-   `kwargs`:
    specifies additional key-word arguments.
    Such as `kwargs={"a": "foo"}`.

**return**:
nothing.


#   Slave class


##  zktx.Slave

**syntax**:
`zktx.Slave(zke, storage)`

Sync data from Zookeeper to the `storage`.

**arguments**:

-   `zke`:
    must be a `zkutil.KazooClientExt` instance.

-   `storage`:
    the instance that user specifies.
    It must provide 4 methods(`apply_jour`, `apply_record`, `add_to_txidset`, `set_txidset`)
    like `zktx.RedisStorage`.



### zktx.Slave.apply

**syntax**:
`zktx.Slave.apply()`

Write all update to the `storage` if there are uncommitted txids.

**return**:
nothing.

```
from pykit import zktx
from pykit import zkutil

storage = zktx.RedisStorage(redis_cli, 'txidset')
zke, _ = zkutil.kazoo_client_ext('127.0.0.1:2181')

slave = zktx.Slave(zke, storage)
slave.apply()
```


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
