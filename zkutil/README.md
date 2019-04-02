<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Methods](#methods)
  - [zkutil.is_backward_locking](#zkutilis_backward_locking)
    - [Naive dead lock detect:](#naive-dead-lock-detect)
  - [zkutil.lock_id](#zkutillock_id)
  - [zkutil.parse_lock_id](#zkutilparse_lock_id)
  - [zkutil.make_digest](#zkutilmake_digest)
  - [zkutil.make_acl_entry](#zkutilmake_acl_entry)
  - [zkutil.make_kazoo_digest_acl](#zkutilmake_kazoo_digest_acl)
  - [zkutil.parse_kazoo_acl](#zkutilparse_kazoo_acl)
  - [zkutil.perm_to_long](#zkutilperm_to_long)
  - [zkutil.perm_to_short](#zkutilperm_to_short)
  - [zkutil.close_zk](#zkutilclose_zk)
- [Conditioned access methods](#conditioned-access-methods)
  - [zkutil.get_next](#zkutilget_next)
  - [zkutil.wait_absent](#zkutilwait_absent)
- [ACID methods](#acid-methods)
  - [zkutil.cas_loop](#zkutilcas_loop)
- [Other methods](#other-methods)
  - [zkutil.init_hierarchy](#zkutilinit_hierarchy)
  - [zkutil.export_hierarchy](#zkutilexport_hierarchy)
- [Exceptions](#exceptions)
  - [zkutil.LockTimeout](#zkutillocktimeout)
- [Classes](#classes)
  - [zkutil.ZKConf](#zkutilzkconf)
  - [zkutil.ZKLock](#zkutilzklock)
    - [Synopsis](#synopsis)
    - [Why we need this](#why-we-need-this)
    - [zkutil.ZKLock.acquire](#zkutilzklockacquire)
    - [zkutil.ZKLock.acquire_loop](#zkutilzklockacquire_loop)
    - [zkutil.ZKLock.try_acquire](#zkutilzklocktry_acquire)
    - [zkutil.ZKLock.try_release](#zkutilzklocktry_release)
    - [zkutil.ZKLock.release](#zkutilzklockrelease)
  - [zkutil.CachedReader](#zkutilcachedreader)
    - [zkutil.CachedReader.watch](#zkutilcachedreaderwatch)
    - [zkutil.CachedReader.close](#zkutilcachedreaderclose)
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


##  zkutil.is_backward_locking

**syntax**:
`zkutil.is_backward_locking(locked_keys, key)`

Check if the operation of locking `key` is a backward-locking.

### Naive dead lock detect:

Locks must be acquired in alphabetic order(or other order, from left to right.
Trying to acquire a `lock>=right_most_locked`, is a forward locking Otherwise it
is a backward locking.

Always do forward locking we can guarantee there won't be a dead lock.
Since a deadlock needs at least one backward locking to form a circular dependency.

If a process fails to acquire a lock in a backward locking,
it should release all locks it holds and redo the entire transaction.

E.g. suppose X has acquired lock a and c, Y has acquired lock b:

```
         Acquired locks by process X and Y
         locks are ordered left-to-right
---------------------------------------------
proc-X   a(locked)                  c(locked)
proc-Y               b(locked)
```

If
X tries to acquire b(**backward**),
Y tries to acquire c(forward):
    There is a deadlock. X should release all locks.

```
---------------------------------------------
proc-X   a(locked)   .------------ c(locked)
                     v             ^
proc-Y               b(locked) ----'
```

If
X tries to acquire b(**backward**)
Y tries to acquires a(**backward**)
    There is a deadlock, X and Y should both release their locks.

```
---------------------------------------------
proc-X   a(locked)   .------------ c(locked)
         ^           v
proc-Y   '---------- b(locked)
```

**arguments**:

-   `locked_keys`:
    is a collection support `in` operator that contains already locked keys.

-   `key`:
    is the key to lock.

**return**:
a `bool` indicate if locking `key` would be a backward-locking.


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
    "counter": <integer>,
    "txid": "<txid>",
}
```

`process_id` and `counter` is `int`, the others are `string`s.

If any of these three field can not be parsed correctly, it will be `None`.

If `node_id` is in form of `txid:...`, `txid` is filled with the text after `:`.
Otherwise it is `None`.
This is added for zk-transaction implementation.

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


##  zkutil.make_kazoo_digest_acl

**syntax**:
`zkutil.make_kazoo_digest_acl(acl)`

Convert tuple/list acl to kazoo style.

E.g.:

```python
acl = (('xp', '123', 'cdrwa'),
       ('foo', 'passw', 'rw'),

print zkutil.make_kazoo_digest_acl(acl)
"""
[
    ACL(perms=12, acl_list=['CREATE', 'DELETE'],
        id=Id(scheme='digest', id=u'foo:VNy+Z9IdXrOUk9Rtia4fQS071t4=')),
    ACL(perms=31, acl_list=['ALL'],
        id=Id(scheme='digest', id=u'xp:LNcZO17uqqJ4GuYoSclIsGjYniQ='))
]
"""
```

**arguments**:

-   `acl`:
    acl in tuple or list.

**return**:
a `list` of `kazoo.security.ACL`.


##  zkutil.parse_kazoo_acl

**syntax**:
`zkutil.parse_kazoo_acl(acls)`

Convert kazoo style acls in list/tuple to a list in form `[(<scheme>, <user>, <perm>)]`.

E.g.:

```python
acls = [ACL(perms=31, acl_list=['ALL'], id=Id(scheme=u'world', id=u'anyone')),
        ACL(perms=5, acl_list=['READ', 'CREATE'],
        id=Id(scheme='digest', id=u'foo:Zu5Tckgnn822Oi3gy2jMA7auDdE='))]

print zkutil.parse_kazoo_acl(acls)
"""
[('world', 'anyone', 'cdrwa'), ('digest', 'foo', 'rc')]
"""
```

**arguments**:

-   `acls`:
    a list/tuple of `kazoo.security.ACL`.

**return**:
a list of acl in form `[(<scheme>, <user>, <perm>)]`


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


##  zkutil.close_zk

**syntax**:
`zkutil.close_zk(zk)`

Stop and close a zk client.

**arguments**:

-   `zk`:
    a `KazooClient` or `KazooClientExt` instance, otherwise raise a `TypeError`.

**return**:
nothing


#   Conditioned access methods

A collection of helper functions those block until a condition satisfied before
returning.
Such as:

-   Wait for a zk-node to be absent.
-   Wait for a zk-node version greater than a specified one before returning
    the node value.

These methods share the same form: `def xxx(zkclient, path, timeout=None, **kwargs)`.

Common parameters are:

-   `zkclient`:
    kazoo client.

-   `path`:
    specifies the path to watch.

-   `timeout`:
    specifies the time(in second) to wait.

    By default it is `None` which means to wait for a year.

    If condition was not satisfied in `timeout` seconds,
    it raises a `ZKWaitTimeout` exception.


##  zkutil.get_next

**syntax**:
`zkutil.get_next(zkclient, path, timeout=None, version=-1)`

Wait until zk-node `path` version becomes greater than `version` then return
node value and `zstat`.

**arguments**:

-   `version`:
    the version that `path` version must be greater than.

**return**:
zk node value and `zstat`.


##  zkutil.wait_absent

**syntax**:
`zkutil.wait_absent(zkclient, path, timeout=None)`

Wait at most `timeout` seconds for zk-node `path` to be absent.

If `path` does not exist, it returns at once.

**return**:
Nothing


#   ACID methods

##  zkutil.cas_loop

**syntax**:
`zkutil.cas_loop(zkclient, path, json=True)`

A helper generator for doing CAS(check and set or compare and swap) on zk.
See [CAS](https://en.wikipedia.org/wiki/Compare-and-swap)

A general CAS loop is like following(check the version when update):

```python
while True:
    curr_val, zstat = zkclient.get(path)
    new_val = curr_val + ':foo'
    try:
        zkclient.set(path, new_val, version=zstat.version)
    except BadVersionError as e:
        continue
    else:
        return
```

`cas_loop` simplifies the above workflow to:

```python
for curr_val, set_val in zkutil.cas_loop(zkclient, path):
    set_val(curr_val + ':foo')
```

The loop body runs several times until a successful update is made to zk.

**arguments**:

-   `zkclient`:
    is a `KazooClient` instance connected to zk.

    It can also be a string, in which case it is treated as a comma separated
    hosts list, and a `zkclient` is created with default setting.

    It can also be a `dict` or an instance of `ZKConf`, in which case it create
    a `zkclient` with `ZKConf` defined setting.


-   `path`:
    is the zk-node path to get and set.

-   `json`:
    whether to do a json load after reading the value from zk and to do a json dump
    before updating the value to zk.

    By default it is `True`.

**return**:
a generator yields a `tuple` of 2 element:

-   The current value,
-   and a function for user to update new value.

This generator stops when a success update committed to zk.


#   Other methods


##  zkutil.init_hierarchy

**syntax**:
`zkutil.init_hierarchy(hosts, hierarchy, users, auth)`

It initialize a zookeeper cluster, including initializing the tree structure, setting value and permissions for each node.

**arguments**:

-   `hosts`:
    comma-separated list of hosts to connect to, such as `'127.0.0.1:2181,127.0.0.1:2182,[::1]:2183'`.

-   `hierarchy`:
    a dict of zk node structure with value or acl optional for each node.
    For example,
    ```
    node1:
      __val__: "json, optional, by default a '{}'"
      __acl__: # optional, same with parent if not given
        user_1: "cdrwa"
        user_2: "rw"
                    ...
    node2:
        node21: {...}
    ```
    As shown above, each node has two attributes `__val__` and `__acl__` which are used to set the corresponding node.

-   `users`:
    a dict in form `{<username>: <password>}` containing all users in `hierarchy`.

-  `auth`:
    a tuple in form `(<scheme>, <user>, <password>)`.
    It is the authorization info to connect to zookeeper which is used to initialize the zookeeper cluster.

**return**:
None.


## zkutil.export_hierarchy

**syntax**:
`def export_hierarchy(zkcli, zkpath)`

Exporting a zookeeper node in a tree structure, and you can import the data into zookeeper using `zkutil.init_hierarchy`

**arguments**:

-   `zkclient`:
    is a `KazooClient` instance connected to zk.

- `zkpath`:
    is zookeeper root path that you want export

#  Exceptions

## zkutil.LockTimeout

Raise if `ZKLock` timed out on waiting to acquire a lock.


#  Classes


##  zkutil.ZKConf

**syntax**:
`zkutil.ZKConf(hosts=None,
               journal_dir=None,
               record_dir=None,
               lock_dir=None,
               node_id=None,
               auth=None,
               acl=None
)`

It is a config wrapper, provding several method for accessing config.
If one of the config field is not spedified when initializing this class, it
falls back to using `config.zk_<field>`.

Classes in this module relies on this class to access config.

E.g.:

```python
config.zk_journal_dir = "my_dir/"
c = zkutil.ZKConf(hosts="127.0.0.1:9999")
c.hosts()       # "127.0.0.1:9999" # specified
c.journal_dir() # "my_dir/"        # by default using `config.zk_<field>`
```


##  zkutil.ZKLock

**syntax**:
`zkutil.ZKLock(lock_name, zkclient=None, zkconf=None, on_lost=None,
               ephemeral=True, timeout=10)`

ZKLock implements a zookeeper based distributed lock.


### Synopsis

Using default configuration:

```python
"""
config.zk_acl      # (('xp', '123', 'cdrwa'), ('foo', 'bar', 'rw'))
config.zk_auth     # ('digest', 'xp', '123')
config.zk_hosts    # '127.0.0.1:2181'
config.zk_node_id  # 'web-01'
config.zk_lock_dir # 'lock/'
"""
with zkutil.ZKLock('foo_lock', on_lost=my_callback):
    do_something()
```

Specify connection arguments. When locks of one of them, use the value defined
in `config.py`.

```python
with zkutil.ZKLock('foo_lock', on_lost=my_callback,
                   zkconf=dict(
                       hosts='127.0.0.1:2181',
                       acl=(('xp', '123', 'cdrwa'),),
                       auth=('digest', 'xp', '123'),
                       node_id='web-3',
                       lock_dir='my_locks/'
                   )):
    do_something()
```

Pass in a `KazooClient`.
Before pass it to `ZKLock`, you should deal with these things:

-   Add node state change listener, to deal with connection issue.
    If connection lost, you should stop doing everything within the lock.
    Because zookeeper might have deleted the zk-node for lock and other process
    the could acquire the lock.

-   `add_auth` after connecting to zk.

```python
self.zk = KazooClient(hosts='127.0.0.1:2181')
self.zk.start()
self.zk.add_auth('digest', 'xp:123')
with zkutil.ZKLock('foo_lock', ...):
    do_something();
```


### Why we need this

It is similar to standard zookeeper mechanism except:

> It does not relies on `sequence` node to enqueue lock request.
> But instead, all processes try to create a same zk-node to acquire the lock.
> Thus it does not guarantee a lock will be acquired in order.
> And it might starve processes.
>
> `sequence` node based lock requires a dir for each lock.
> Thus it is not suitable in case there are a lot locks.
>
> And a single node lock is much easier if you'd like to retrieve lock holders
> info.

**arguments**:

-   `lock_name`:
    the lock name.
    It is used as part of zk-node to create.

-   `zkclient`:
    is a `KazooClient` instance connected to zk.

    If this argument  is not `None`, `hosts` and `auth` are ignored.

    If this argument is `None`, `on_lost` must be specified to watch lock node
    state change event. And connection is maintained by `ZKLock` and will be
    destroyed at once after lock released.

-   `zkconf`:
    is a `ZKConf` or a `dict` contains zk config.

-   `zkconf:node_id`:
    is used to identify a host.

    Different host must have different `node_id`.
    Or it can not differentiate what host a node belongs to, during reconnecting
    to zk.

    By default it uses `config.zk_node_id`

    > Why this?
    >   ZKLock sends a `create` command to zk to acquire a lock.
    >   But it is possible a process successfully created a node but did not
    >   receive a success response(with a node left on server).
    >   In this case we always re-get the node, no matter whether we received
    >   the response of the creation.
    >   And check node value(with node_id embedded in it), to see if this
    >   zk-node is created by this host.

-   `zkconf:hosts`:
    is a comma separated address list to specify zookeeper cluster, such as:
    `127.0.0.1:2181,128.0.0.2:2181`

    If it is `None`, and `zkclient` is `None`, `ZKLock` tries to use
    `config.zk_hosts` to establish a connection.

-   `on_lost`:
    is a `callable` that accepts no argument to handle connection state change
    event.
    Such as:

    ```python
    def my_on_lost():
        sys.exit()

    with zkutil.ZKLock('foo_lock', on_lost=my_on_lost):
        do_something()
    ```

-   `zkconf:acl`:
    is a two level tuple to specify the ACL for creating a lock node.

    `acl` can specify access control config for multi users, such as:
    `(('xp', 'xp-s-password', 'cdrwa'), ('other', 'password', 'r'))`

    If it is `None`, `ZKLock` uses `config.zk_acl` for created node.

-   `zkconf:auth`:
    is the authorization info to connect to zookeeper.
    It is used only when `zkclient` is `None`.

    If it is `None`, `ZKLock` uses `config.zk_auth` to connect.

-   `zkconf:lock_dir`:
    specifies base dir of lock node.
    Such as `/mycluster/mylocks/`.

    If it is `None`, `ZKLock` uses `config.zk_lock_dir`.

    If `config.zk_lock_dir` is `None` it uses a predefined const: `lock/`.

-   `identifier`:
    specifies a lock identifier in str or dict with `id` and `val`,
    which `id` is used to check if a process has been holding a lock.

    **Two different processes must specifies different identifier**.

    By default it is `None`, in which case `ZKLock` will generate one.

    A recovered process would uses a specified identifier.

-   `ephemeral`:
    specifies if the lock will be cleared when connection to zk lost.
    A persistent lock is implemented with a normal zk-node.
    A ephemeral lock is implemented with a `ephemeral` zk-node.

    By default it is `True`.

    > A persistent lock is used in cases when you need to accurately track
    > locking state, such as when detecting which resource has been locked by a
    > dead transaction.
    > Unless **You Know What You Are Doing**,
    > do **NOT** use a persistent lock, because there must be a cleanup program
    > for making thing right.

-   `timeout`:
    is a `float` that specifies how long in second to wait acquiring a lock.

    By default it is 10(second).


###  zkutil.ZKLock.acquire

**syntax**:
`ZKLock.acquire(timeout=None)`

Acquire the lock in blocking mode.

**arguments**:

-   `timeout`:
    is `float` time in second to wait.
    If it is `None`, it use `self.timeout`, which is 10 seconds by default.

    If `timeout` is less than 0 `ZKLock` tries to acquire the lock for only once
    and if failed, it raise `LockTimeout` at once.

**return**:
Nothing


###  zkutil.ZKLock.acquire_loop

**syntax**:
`zkutil.ZKLock.acquire_loop(timeout=None)`

It returns a generator that yields tuple of lock-holder-id(`identifier`) and
lock node version, if lock is held by others.

Once lock is acquired, this generator stops.

This generator provides a way to customize behaviors during blocking acquiring.

**Synopsis**:

```python
lock = zkutil.ZKLock('foo')
try:
    for holder, ver in lock.acquire_loop(timeout=3):
        print 'lock is currently held by:', holder, ver

    print 'lock is acquired'
except zkutil.LockTimeout as e:
    print 'timeout to acquire "foo"'
```

**arguments**:

-   `timeout`:
    specifies the max time in second to wait.

**return**:
a `generator`

###  zkutil.ZKLock.try_acquire

**syntax**:
`ZKLock.try_acquire()`

Try to acquire the lock and return result.
It never blocks.

**return**:
a tuple of result, lock holder and lock holder version.
Such as `(True, "aa-xx-bb", -1)` or `(False, "aa-xx-cc", 12)`

If lock is acquired:
- the 1st element is `True`,
- the 2nd is identifier of this lock,
- the 3rd is `-1`.

If lock is not acquired:
- the 1st element is `False`,
- the 2nd is identifier of the lock holder,
- the 3rd is a non-negative integer, which is the version of the zk node.


###  zkutil.ZKLock.try_release

**syntax**:
`ZKLock.try_release()`

Release lock if current lock holder is this lock.
It never blocks.

**return**:
a tuple of result, lock holder and lock holder version.
Such as `(True, "aa-xx-bb", -1)` or `(False, "aa-xx-cc", 12)`

If lock holder is this `ZKLock`(checked by identifier), or lock is not acquired
by anyone):

- the 1st element is `True`,
- the 2nd is identifier of this lock,
- the 3rd is `-1` or `zstat.version` or the lock zknode.

Otherwise:

- the 1st element is `False`,
- the 2nd is identifier of the lock holder,
- the 3rd is a non-negative integer, which is the version of the zk node.


###  zkutil.ZKLock.release

**syntax**:
`ZKLock.release()`

Release the lock if it has been locked.
Otherwise return silently.

If this lock initiated a connection by itself, it will be closed.

**return**:
Nothing


##  zkutil.CachedReader

**syntax**:
`zkutil.CachedReader(zk, path, callback=None)`

A subclass of `dict`, cache the data in zookeeper.
The type of data must be `dict`.

```
#bar = {
#    'jobs': {
#        'num' : 10
#    }
#}
cr = CachedReader('127.0.0.1:2181', 'bar')
for i in range(cr['jobs']['num']):
    doit()
```

**arguments**:

-   `zk`:
    is the connection argument, which can be:

    -   Comma separated host list, such as
        `"127.0.0.1:2181,127.0.0.2:2181"`.

    -   A `zkutil.ZKConf` instance specifying connection argument with other
        config.

    -   A plain `dict` to create a `zkutil.ZKConf` instance.

-   `path`:
    the path of the node in zookeeper.

-   `callback`:
    give a callback when the node change. Defaults to `None`.
    It has 3 arguments `(path, old_dict, new_dict)`.


### zkutil.CachedReader.watch

**syntax**:
`zkutil.CachedReader.watch(timeout=None)`

Wait until the node change and return a list `[old_dict, new_dict]`.
If timeout, raise a `ZKWaitTimeout`.

**arguments**:

-   `timeout`:
    specifies the time(in second) to wait.
    By default it is `None` which means to wait for a year

**return**:
If close the `CachedReader` by `zkutil.CachedReader.close()`, it return `None`.
If the node change, it return a list `[old_dict, new_dict]`


### zkutil.CachedReader.close

**syntax**:
`zkutil.CachedReader.close()`

Stop the `zkutil.CachedReader.watch` and the callback.


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
