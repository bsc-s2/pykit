<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Exceptions](#exceptions)
  - [etcd.EtcdException](#etcdetcdexception)
  - [etcd.EtcdInternalError](#etcdetcdinternalerror)
  - [etcd.NoMoreMachineError](#etcdnomoremachineerror)
  - [etcd.EtcdReadTimeoutError](#etcdetcdreadtimeouterror)
  - [etcd.EtcdRequestError](#etcdetcdrequesterror)
  - [etcd.EtcdResponseError](#etcdetcdresponseerror)
  - [etcd.EtcdIncompleteRead](#etcdetcdincompleteread)
  - [etcd.EtcdSSLError](#etcdetcdsslerror)
  - [etcd.EtcdWatchError](#etcdetcdwatcherror)
  - [etcd.EtcdKeyError](#etcdetcdkeyerror)
  - [etcd.EtcdValueError](#etcdetcdvalueerror)
  - [etcd.EcodeKeyNotFound](#etcdecodekeynotfound)
  - [etcd.EcodeTestFailed](#etcdecodetestfailed)
  - [etcd.EcodeNotFile](#etcdecodenotfile)
  - [etcd.EcodeNotDir](#etcdecodenotdir)
  - [etcd.EcodeNodeExist](#etcdecodenodeexist)
  - [etcd.EcodeRootROnly](#etcdecoderootronly)
  - [etcd.EcodeDirNotEmpty](#etcdecodedirnotempty)
  - [etcd.EcodePrevValueRequired](#etcdecodeprevvaluerequired)
  - [etcd.EcodeTTLNaN](#etcdecodettlnan)
  - [etcd.EcodeIndexNaN](#etcdecodeindexnan)
  - [etcd.EcodeInvalidField](#etcdecodeinvalidfield)
  - [etcd.EcodeInvalidForm](#etcdecodeinvalidform)
  - [etcd.EcodeInscientPermissions](#etcdecodeinscientpermissions)
- [Constants](#constants)
  - [etcd.EtcdKeysResult.key](#etcdetcdkeysresultkey)
  - [etcd.EtcdKeysResult.value](#etcdetcdkeysresultvalue)
  - [etcd.EtcdKeysResult.expiration](#etcdetcdkeysresultexpiration)
  - [etcd.EtcdKeysResult.ttl](#etcdetcdkeysresultttl)
  - [etcd.EtcdKeysResult.modifiedIndex](#etcdetcdkeysresultmodifiedindex)
  - [etcd.EtcdKeysResult.createdIndex](#etcdetcdkeysresultcreatedindex)
  - [etcd.EtcdKeysResult.newKey](#etcdetcdkeysresultnewkey)
  - [etcd.EtcdKeysResult.dir](#etcdetcdkeysresultdir)
  - [etcd.EtcdKeysResult.leaves](#etcdetcdkeysresultleaves)
  - [etcd.Client.base_uri](#etcdclientbase_uri)
  - [etcd.Client.host](#etcdclienthost)
  - [etcd.Client.port](#etcdclientport)
  - [etcd.Client.protocol](#etcdclientprotocol)
  - [etcd.Client.read_timeout](#etcdclientread_timeout)
  - [etcd.Client.allow_redirect](#etcdclientallow_redirect)
  - [etcd.Client.machines](#etcdclientmachines)
  - [etcd.Client.members](#etcdclientmembers)
  - [etcd.Client.leader](#etcdclientleader)
  - [etcd.Client.version](#etcdclientversion)
  - [etcd.Client.st_leader](#etcdclientst_leader)
  - [etcd.Client.st_self](#etcdclientst_self)
  - [etcd.Client.st_store](#etcdclientst_store)
  - [etcd.Client.names](#etcdclientnames)
  - [etcd.Client.ids](#etcdclientids)
  - [etcd.Client.clienturls](#etcdclientclienturls)
  - [etcd.Client.peerurls](#etcdclientpeerurls)
- [Classes](#classes)
  - [etcd.EtcdKeysResult](#etcdetcdkeysresult)
  - [etcd.Client](#etcdclient)
- [Methods](#methods)
  - [etcd.EtcdKeysResult.get_subtree](#etcdetcdkeysresultget_subtree)
  - [etcd.EtcdKeysResult.__eq__](#etcdetcdkeysresult__eq__)
  - [etcd.EtcdKeysResult.__ne__](#etcdetcdkeysresult__ne__)
  - [etcd.EtcdKeysResult.__repr__](#etcdetcdkeysresult__repr__)
  - [etcd.Client.read](#etcdclientread)
  - [etcd.Client.get](#etcdclientget)
  - [etcd.Client.write](#etcdclientwrite)
  - [etcd.Client.set](#etcdclientset)
  - [etcd.Client.test_and_set](#etcdclienttest_and_set)
  - [etcd.Client.update](#etcdclientupdate)
  - [etcd.Client.delete](#etcdclientdelete)
  - [etcd.Client.test_and_delete](#etcdclienttest_and_delete)
  - [etcd.Client.watch](#etcdclientwatch)
  - [etcd.Client.eternal_watch](#etcdclienteternal_watch)
  - [etcd.Client.mkdir](#etcdclientmkdir)
  - [etcd.Client.refresh](#etcdclientrefresh)
  - [etcd.Client.lsdir](#etcdclientlsdir)
  - [etcd.Client.rlsdir](#etcdclientrlsdir)
  - [etcd.Client.deldir](#etcdclientdeldir)
  - [etcd.Client.rdeldir](#etcdclientrdeldir)
  - [etcd.Client.add_member](#etcdclientadd_member)
  - [etcd.Client.del_member](#etcdclientdel_member)
  - [etcd.Client.change_peerurls](#etcdclientchange_peerurls)
  - [etcd.Client.create_root](#etcdclientcreate_root)
  - [etcd.Client.enable_auth](#etcdclientenable_auth)
  - [etcd.Client.disable_auth](#etcdclientdisable_auth)
  - [etcd.Client.create_user](#etcdclientcreate_user)
  - [etcd.Client.create_role](#etcdclientcreate_role)
  - [etcd.Client.get_user](#etcdclientget_user)
  - [etcd.Client.get_role](#etcdclientget_role)
  - [etcd.Client.grant_user_roles](#etcdclientgrant_user_roles)
  - [etcd.Client.revoke_user_roles](#etcdclientrevoke_user_roles)
  - [etcd.Client.grant_role_permissions](#etcdclientgrant_role_permissions)
  - [etcd.Client.revoke_role_permissions](#etcdclientrevoke_role_permissions)
  - [etcd.Client.delete_user](#etcdclientdelete_user)
  - [etcd.Client.delete_role](#etcdclientdelete_role)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

etcd client

#   Status

The library is considered production ready.

#   Synopsis

```python
from pykit import etcd

hosts=(
    ('192.168.0.100', 2379),
    ('192.168.0.101', 2379),
    ('192.168.0.102', 2379),
)

try:
    c = etcd.Client(host=hosts)
    c.set('test_key', 'test_val')
    res = c.get('test_key')
    # type(res) is EtcdKeysResult
    # res.key == 'test_key'
    # res.value == 'test_val'
    # res.dir == False
    # ...

    c.st_leader
    # out type is `dict`
    # {
    #   "leader": "991200c666cc4678",
    #   "followers":{
    #       "183ebbe2e22ee250": {
    #           "latency": {
    #               "current": 0.00095,
    #               "average": 0.09798531413612557,
    #               "standardDeviation": 1.3282931634902915,
    #               "minimum": 0.000635,
    #               "maximum": 18.407235
    #           },
    #           "counts": {
    #               "fail": 0,
    #               "success": 191
    #           }
    #       },
    #       "291578612bc6deb": {
    #           "latency": {
    #               "current": 0.000949,
    #               "average": 0.001928250000000001,
    #               "standardDeviation": 0.0018525034545722491,
    #               "minimum": 0.000876,
    #               "maximum": 0.017505
    #           },
    #           "counts": {
    #               "fail": 0,
    #               "success": 188
    #           }
    #       },
    #   }
    # }

    c.st_self
    # out type is `dict`
    #   {
    #       "name": "node_1",
    #       "id": "991200c666cc4678",
    #       "state": "StateLeader",
    #       "startTime": "2017-06-14T05:20:04.334273309Z",
    #       "leaderInfo": {
    #           "leader": "991200c666cc4678",
    #           "uptime": "4h41m55.43860796s",
    #           "startTime": "2017-06-14T05:20:04.477688456Z"
    #       },
    #       "recvAppendRequestCnt": 0,
    #       "sendAppendRequestCnt": 736
    #   }

    c.st_store
    # out type is `dict`
    #   {
    #       "getsSuccess": 4,
    #       "getsFail": 7,
    #       "setsSuccess": 53,
    #       "setsFail": 0,
    #       "deleteSuccess": 24,
    #       "deleteFail": 2,
    #       "updateSuccess": 2,
    #       "updateFail": 0,
    #       "createSuccess": 7,
    #       "createFail": 1,
    #       "compareAndSwapSuccess": 3,
    #       "compareAndSwapFail": 1,
    #       "compareAndDeleteSuccess": 0,
    #       "compareAndDeleteFail": 0,
    #       "expireCount": 3,
    #       "watchers": 0
    #   }

    n = c.names
    # get names of etcd servers
    # n=['node1', 'node2', 'node3']

    ids = c.ids
    # get ids of etcd servers
    # ids=['fca771384ed46928', '991200c666cc4678', '4768ce54ee212c95']

    peerurls = ['http://192.168.0.103:2380']
    c.add_member(*peerurls)
    # only register new node
    # after it, start the server

    peerurls = ['http://192.168.0.102:4380']
    c.change_peerurls('fca771384ed46928', *peerurls)
except etcd.EtcdException as e:
    print(repr(e))
```

#   Description

A python client for Etcd https://github.com/coreos/etcd

This module will only work correctly with the etcd server version 2.3.x or later.

#   Exceptions

##  etcd.EtcdException

**syntax**:
`etcd.EtcdException`

The base class of the other exceptions in this module.
It is a subclass of `Exception`.

##  etcd.EtcdInternalError

**syntax**:
`etcd.EtcdInternalError`

A subclass of `etcd.EtcdException`.
Raise if etcd server "Raft Internal Error" or "During Leader Election".

##  etcd.NoMoreMachineError

**syntax**:
`etcd.NoMoreMachineError`

A subclass of `etcd.EtcdException`.
Raise if there are no machines left to try.

##  etcd.EtcdReadTimeoutError

**syntax**:
`etcd.EtcdReadTimeoutError`

A subclass of `etcd.EtcdException`.
Raise if timeout when watching a key.

##  etcd.EtcdRequestError

**syntax**:
`etcd.EtcdRequestError`

A subclass of `etcd.EtcdException`.
Raise if the http request is invalid.
Such as invalid http request method or invalid headers.

##  etcd.EtcdResponseError

**syntax**:
`etcd.EtcdResponseError`

A subclass of `etcd.EtcdException`.
Raise if etcd server failed to process request.

##  etcd.EtcdIncompleteRead

**syntax**:
`etcd.EtcdIncompleteRead`

A subclass of `etcd.EtcdException`.
Raise if the encoding of response body is not json.

##  etcd.EtcdSSLError

**syntax**:
`etcd.EtcdSSLError`

A subclass of `etcd.EtcdException`.
Raise if the protocol is `https`.
Right now, this module don't support `https`.

##  etcd.EtcdWatchError

**syntax**:
`etcd.EtcdWatchError`

A subclass of `etcd.EtcdException`.
Raise if "watcher is cleared due to etcd recovery"
or "The event in requested index is outdated and cleared".

##  etcd.EtcdKeyError

**syntax**:
`etcd.EtcdKeyError`

A subclass of `etcd.EtcdException` and `KeyError`.
The base class of `etcd.EcodeKeyNotFound`, `etcd.EcodeNotFile`,
`etcd.EcodeNotDir` and `etcd.EcodeNodeExist` in this module.

##  etcd.EtcdValueError

**syntax**:
`etcd.EtcdValueError`

A subclass of `etcd.EtcdException` and `ValueError`.
The base class of `etcd.EcodeTestFailed`, `etcd.EcodeRootROnly`,
`etcd.EcodeDirNotEmpty`, `etcd.EcodePrevValueRequired`,
`etcd.EcodeTTLNaN`, `etcd.EcodeIndexNaN`, `etcd.EcodeInvalidField` and
`etcd.EcodeInvalidForm` in this module.

##  etcd.EcodeKeyNotFound

**syntax**:
`etcd.EcodeKeyNotFound`

A subclass of `etcd.EtcdKeyError`.
Raise if key not found.

##  etcd.EcodeTestFailed

**syntax**:
`etcd.EcodeTestFailed`

A subclass of `etcd.EtcdValueError`.
Raise if compare failed.
Such as `prevValue=abc` compare failed in the cluster.

##  etcd.EcodeNotFile

**syntax**:
`etcd.EcodeNotFile`

A subclass of `etcd.EtcdKeyError`.
Raise if the file operation to a dir.

##  etcd.EcodeNotDir

**syntax**:
`etcd.EcodeNotDir`

A subclass of `etcd.EtcdKeyError`.
Raise if the dir operation to a file.

##  etcd.EcodeNodeExist

**syntax**:
`etcd.EcodeNodeExist`

A subclass of `etcd.EtcdKeyError`.
Raise if create a existed key with `prevExist=False`.

##  etcd.EcodeRootROnly

**syntax**:
`etcd.EcodeRootROnly`

A subclass of `etcd.EtcdValueError`.
Raise if root is read only.

##  etcd.EcodeDirNotEmpty

**syntax**:
`etcd.EcodeDirNotEmpty`

A subclass of `etcd.EtcdValueError`.
Raise if delete a not empty dir with `recursive=false`.

##  etcd.EcodePrevValueRequired

**syntax**:
`etcd.EcodePrevValueRequired`

A subclass of `etcd.EtcdValueError`.
Raise if not provide `prevValue` when it is required in post form.

##  etcd.EcodeTTLNaN

**syntax**:
`etcd.EcodeTTLNaN`

A subclass of `etcd.EtcdValueError`.
Raise if the given `TTL` in post form is not a number.

##  etcd.EcodeIndexNaN

**syntax**:
`etcd.EcodeIndexNaN`

A subclass of `etcd.EtcdValueError`.
Raise if the given `index` in post form is not a number.

##  etcd.EcodeInvalidField

**syntax**:
`etcd.EcodeInvalidField`

A subclass of `etcd.EtcdValueError`.
Raise if the http header field is invalid.

##  etcd.EcodeInvalidForm

**syntax**:
`etcd.EcodeInvalidForm`

A subclass of `etcd.EtcdValueError`.
Raise if post form is invalid.

##  etcd.EcodeInscientPermissions

**syntax**:
`etcd.EcodeInscientPermissions`

A subclass of `etcd.EtcdException`.
Raise if Unauthorized.

#   Constants

##  etcd.EtcdKeysResult.key

**syntax**:
`etcd.EtcdKeysResult.key`

The current node key. Defaults to `None`.

##  etcd.EtcdKeysResult.value

**syntax**:
`etcd.EtcdKeysResult.value`

The current node value. Defaults to `None`.

##  etcd.EtcdKeysResult.expiration

**syntax**:
`etcd.EtcdKeysResult.expiration`

Type is `str`, the current node expire time. Defaults to `None`.

##  etcd.EtcdKeysResult.ttl

**syntax**:
`etcd.EtcdKeysResult.ttl`

The left seconds of the current node.
If `None`, it is a permanent node. Defaults to `None`.

##  etcd.EtcdKeysResult.modifiedIndex

**syntax**:
`etcd.EtcdKeysResult.modifiedIndex`

Type is `int`, modified index of the node returned from server.

##  etcd.EtcdKeysResult.createdIndex

**syntax**:
`etcd.EtcdKeysResult.createdIndex`

Type is `int`, created index of the node returned from server.

##  etcd.EtcdKeysResult.newKey

**syntax**:
`etcd.EtcdKeysResult.newKey`

Whether the node is created in this request.
Type is `bool`, defaults to `False`.

##  etcd.EtcdKeysResult.dir

**syntax**:
`etcd.EtcdKeysResult.dir`

Whether the node is a dir or not.
Type is `bool`, defaults to `False`.

##  etcd.EtcdKeysResult.leaves

**syntax**:
`etcd.EtcdKeysResult.leaves`

The nodes which have value.
It is an iterator. Each element is a `etcd.EtcdKeysResult` object.

##  etcd.Client.base_uri

**syntax**:
`etcd.Client.base_uri`

Type is `str`, the default etcd server clienturl.

##  etcd.Client.host

**syntax**:
`etcd.Client.host`

Type is `str`, the default etcd server ip.
Defaults to `127.0.0.1`.

##  etcd.Client.port

**syntax**:
`etcd.Client.port`

Type is `int`, the port used to connect to etcd server.
Defaults to `2379`.

##  etcd.Client.protocol

**syntax**:
`etcd.Client.protocol`

Type is `str`, protocol used to connect etcd server.
Only support http, defaults to `http`.

##  etcd.Client.read_timeout

**syntax**:
`etcd.Client.read_timeout`

Max seconds to wait for a request.
Type is `int`, defaults to `10`.

##  etcd.Client.allow_redirect

**syntax**:
`etcd.Client.allow_redirect`

Type is `bool`, allow the client to connect other nodes.
Defaults to `True`.

##  etcd.Client.machines

**syntax**:
`etcd.Client.machines`

Members of the cluster.
Type is `list`, like `['http://127.0.0.1:4001', 'http://127.0.0.1:4002']`.

##  etcd.Client.members

**syntax**:
`etcd.Client.members`

A more structured view of peers in the cluster.
Type is `list`, like

```python
[
    {
      "id": "291578612bc6deb",
      "name": "node_0",
      "peerURLs": [
        "http://192.168.52.30:3380"
      ],
      "clientURLs": [
        "http://192.168.52.30:3379"
      ]
    },
    {
      "id": "183ebbe2e22ee250",
      "name": "node_2",
      "peerURLs": [
        "http://192.168.52.32:3380"
      ],
      "clientURLs": [
        "http://192.168.52.32:3379"
      ]
    },
]
```

##  etcd.Client.leader

**syntax**:
`etcd.Client.leader`

The leader of the cluster.
Type is `dict`, like
```python
{
    "id":"ce2a822cea30bfca",
    "name":"n",
    "peerURLs":["http://127.0.0.1:2380"],
    "clientURLs":["http://127.0.0.1:4001"]
}
```

##  etcd.Client.version

**syntax**:
`etcd.Client.version`

Version of etcd server.

##  etcd.Client.st_leader

**syntax**:
`etcd.Client.st_leader`

The stats of the leader.
Type is `dict`.

##  etcd.Client.st_self

**syntax**:
`etcd.Client.st_self`

The stats of the local server.
Type is `dict`.

##  etcd.Client.st_store

**syntax**:
`etcd.Client.st_store`

The stats of the kv store.
Type is `dict`.

##  etcd.Client.names

**syntax**:
`etcd.Client.names`

Name of members in the cluster.
Type is `list`.

##  etcd.Client.ids

**syntax**:
`etcd.Client.ids`

Id of members in the cluster.
Type is `list`.

##  etcd.Client.clienturls

**syntax**:
`etcd.Client.clienturls`

ClientUrls of members in the cluster.
Type is `list`.

##  etcd.Client.peerurls

**syntax**:
`etcd.Client.peerurls`

PeerUrls of members in the cluster.
Type is `list`.

#   Classes

## etcd.EtcdKeysResult

**syntax**:
`etcd.EtcdKeysResult(action=None, node=None, prevNode=None)`

**arguments**:

-   `action`:
    The action that resulted in key creation, type is `str`. Defaults to `None`.

-   `node`:
    The dictionary containing all node information, type is `dict`. Defaults to `None`.

-   `prevNode`:
    The dictionary containing previous node information, type is `dict`. Defaults to `None`.


## etcd.Client

Etcd client class.

**syntax**:
`etcd.Client(host='127.0.0.1',
             port=2379,
             version_prefix='/v2',
             read_timeout=10,
             allow_redirect=True,
             protocol='http',
             allow_reconnect=True,
             basic_auth_account=None,
             logger=None,)`

**arguments**:

-   `host`:
    Mixed, if a `str`, it is the IP to connect to.
    If a `tuple` or `list`, like `((ip, port), (ip, port))`.
    Defaults to `127.0.0.1`.

-   `port`:
    Type is `int`, the port used to connect to etcd server.
    Defaults to `2379`.

-   `version_prefix`:
    Type is `str`, url or version prefix in etcd url. Defaults to `v2`.

-   `read_timeout`:
    Type is `int`, max seconds to wait for a request. Defaults to `10`.

-   `allow_redirect`:
    Type is `bool`, allow the client to connect other nodes. Defaults to `True`.

-   `protocol`:
    Type is `str`, right now only support http. Defaults to `http`.

-   `allow_reconnect`:
    Type is `bool`, allow the client to reconnect to another etcd server
    in the cluster in the case the default one does not respond. Defaults to `True`.

-   `basic_auth_account`:
    Type is `str`, the authorization information. Defaults to `None`.

-   `logger`:
    The logger handle, if not provided use the default handle. Defaults to `None`.

#   Methods

##  etcd.EtcdKeysResult.get_subtree

**syntax**:
`etcd.EtcdKeysResult.get_subtree(leaves_only=False)`

Get all the subtree resulting from a `recursive=true` call to etcd.

**arguments**:

-   `leaves_only`:
    If `True`, only value nodes are returned,
    else return all the nodes.

**return**:
It is an iterator. Each element is a `etcd.EtcdKeysResult` object.

##  etcd.EtcdKeysResult.__eq__

**syntax**:
`etcd.EtcdKeysResult.__eq__(other)`

Compare one with another,
if they are same, return `True`, else return `False`

##  etcd.EtcdKeysResult.__ne__

**syntax**:
`etcd.EtcdKeysResult.__ne__(other)`

Compare one with another,
if they are same, return `False`, else return `True`

##  etcd.EtcdKeysResult.__repr__

**syntax**:
`etcd.EtcdKeysResult.__repr__()`

Convert the object to a string and return it.

##  etcd.Client.read

**syntax**:
`etcd.Client.read(key, **argkv)`

Get the value with `key`

**arguments**:

-   `key`:
    The key which wil be accessed.
    `/XXX` is same as `XXX`.

-   `argkv`:
    Other kv args.

    -   `recursive(bool)`:
        Fetch a dir recursively.

    -   `wait(bool)`:
        Wait and return next time the key is changed.

    -   `waitIndex(int)`:
        The index to fetch results from.

    -   `sorted(bool)`:
        Sort the output keys.

    -   `quorum(bool)`:
        If `True`, get value through raft.

    -   `timeout(int)`:
        Max seconds to wait for the request.

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.get

It is same as `etcd.Client.read`.

##  etcd.Client.write

**syntax**:
`etcd.Client.write(key, value=None, ttl=None, dir=False, append=False, refresh=False, **argkv)`

Writes the value for a key, possibly doing atomic Compare-and-Swap.

Raise a `etcd.EtcdRequestError` when `value is not None` and `dir is True`.

**arguments**:

-   `key`:
    The key that will be writen.
    `/XXX` is same as `XXX`.

-   `value`:
    Value to set. Defaults to `None`.

-   `ttl`:
    Time in seconds of expiration (optional).
    Type is `int`. Defaults to `None`.

-   `dir`:
    Set to `True` if we are writing a directory.
    Type is `bool`. Defaults to `False`.

-   `append`:
    If `True`, it will post to append the new value to the dir, creating a sequential key.
    Defaults to false.

-   `refresh`:
    If `True`, only update the ttl, prev key must existed(`prevExist=True`).

-   `argkv`:
    Other kv args.

    -   `prevValue`:
        Compare with this value, and swap only if corresponding (optional).

    -   `prevIndex(int)`:
        Modify key only if actual modifiedIndex matches the provided one (optional).

    -   `prevExist(bool)`:
        If `False`, only create key; if `True`, only update key.

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.set

**syntax**:
`etcd.Client.set(key, value, ttl=None)`

Set `value` with `key`.

**arguments**:

-   `key`:
    See `key` in `etcd.Client.write`.

-   `value`:
    See `value` in `etcd.Client.write`.

-   `ttl`:
    See `ttl` in `etcd.Client.write`.

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.test_and_set

**syntax**:
`etcd.Client.test_and_set(key, value, ttl=None, **argkv)`

Set `value` with `key`.

**arguments**:

-   `key`:
    See `key` in `etcd.Client.write`.

-   `value`:
    See `value` in `etcd.Client.write`.

-   `ttl`:
    See `ttl` in `etcd.Client.write`.

-   `argkv`:
    See other kv args in `etcd.Client.write`.

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.update

**syntax**:
`etcd.Client.update(res)`

Updates the value for a key atomically.

```python
c = etcd.Client(host=hosts)
res = c.read("/somekey")
res.value += 1
c.update(res)
```

**arguments**:

-   `res`:
    A `etcd.EtcdKeysResult` object.

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.delete

**syntax**:
`etcd.Client.delete(key, recursive=None, dir=None, **argkv)`

Remove a key from etcd.

**arguments**:

-   `key`:
    The key which will be delete.

-   `recursive`:
    If we want to recursively delete a directory, set it to `True`.
    Defaults to `None`.

-   `dir`:
    If we want to delete a directory, set it to `True`.
    Defaults to `None`.

-   `argkv`:
    Other kv args.

    -   `prevValue`:
        Compare with this value and delete only if corresponding (optional).

    -   `prevIndex(int)`:
        Delete only if actual modifiedIndex matches the provided one (optional).

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.test_and_delete

**syntax**:
`etcd.Client.test_and_delete(self, key, **argkv)`

Remove a key from etcd.

**arguments**:

-   `key`:
    The key which will be delete.

-   `argkv`:
    See other kv args in `etcd.Client.delete`.

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.watch

**syntax**:
`etcd.Client.watch(self, key, waitindex=None, timeout=None, **argkv)`

Blocks until a new event has been received or timeout.

Raise a `etcd.EtcdReadTimeoutError` if timeout.

**arguments**:

-   `key`:
    The key which will be watched.

-   `waitindex`:
    Index to start from.
    Type is `int`. Defautls to `None`.
    If `None` use the newest index.

-   `timeout`:
    Max seconds to wait.
    If `None`, use `etcd.Client.read_timeout`.
    If `0` means infinite waiting.

-   `argkv`:
    Other kv args.

    -   `recursive(bool)`
        If want to watch a dir, set `True`.

    -   `waitIndex(int)`:
        If `waitindex` is `None`, use it.

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.eternal_watch

**syntax**:
`etcd.Client.eternal_watch(key, waitindex=None, until=None, **argkv)`

Blocks until the modify index of the key is ge than `until`.

**arguments**:

-   `key`:
    See `key` in `etcd.Client.watch`.

-   `waitindex`:
    See `waitindex` in `etcd.Client.watch`.

-   `timeout`:
    See `timeout` in `etcd.Client.watch`.

-   `until`:
    Break the loop when the modify index of the key is ge than it.
    If `None`, the loop will not be break. Defaults to `None`.

-   `argkv`:
    See other kv args in `etcd.Client.watch`.

**return**:
It is an iterator. Each element is a `etcd.EtcdKeysResult` object.

##  etcd.Client.mkdir

**syntax**:
`etcd.Client.mkdir(key, ttl=None)`

Create a dir in the cluster.

**arguments**:

-   `key`:
    The key that will be created.

-   `ttl`:
    Time in seconds of expiration.
    See `ttl` in `etcd.Client.write`.

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.refresh

**syntax**:
`etcd.Client.refresh(key, ttl=None)`

Update the `ttl` of the `key`.

**arguments**:

-   `key`:
    See `key` in `etcd.Client.write`.

-   `ttl`:
    Time in seconds of expiration.
    See `ttl` in `etcd.Client.write`.

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.lsdir

**syntax**:
`etcd.Client.lsdir(key)`

Get all nodes of the dir with `key`.

**arguments**:

-   `key`:
    The key that will be got.
    See `key` in `etcd.Client.read`.

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.rlsdir

**syntax**:
`etcd.Client.rlsdir(key)`

Get all nodes of the dir with `key` recursively.

**arguments**:

-   `key`:
    The key that will be got.
    See `key` in `etcd.Client.read`.

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.deldir

**syntax**:
`etcd.Client.deldir(key)`

Delete a dir in cluster with `key`.

**arguments**:

-   `key`:
    The key that will be deleted.
    See `key` in `etcd.Client.delete`.

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.rdeldir

**syntax**:
`etcd.Client.rdeldir(key)`

Delete a dir in cluster with `key` recursively.

**arguments**:

-   `key`:
    The key that will be deleted.
    See `key` in `etcd.Client.delete`.

**return**:
A `etcd.EtcdKeysResult` object.

##  etcd.Client.add_member

**syntax**:
`etcd.Client.add_member(*peerurls)`

Add a new node in the cluster.

Raise a `etcd.EtcdResponseError` if the cluster fails to process the request.

Raise a `etcd.EtcdException` if the member exists in the cluster
or existed in the cluster at some point in the past
or any of the given peerURLs exists in the cluster.

**arguments**:

-   `peerurls`:
    The new node peerurls.
    Type is `list`, like`['http://127.0.0.1:2380',]`

**return**:
A `dick`, like

```python
{
  "id": "8398eea285fc82be",
  "name": "",
  "peerURLs": [
    "http://10.0.0.10:2380"
  ],
  "clientURLs": []
}
```

##  etcd.Client.del_member

**syntax**:
`etcd.Client.del_member(mid)`

Remove a member from the cluster.

**arguments**:

-   `mid`:
    The id of the node in the cluster.

**return**:
nothing

##  etcd.Client.change_peerurls

**syntax**:
`etcd.Client.change_peerurls(mid, *peerurls)`

Change the peer urls of a given member.

**arguments**:

-   `mid`:
    The id of the node in the cluster.

-   `peerurls`:
    The peerurls that will be set to the member.
    Type is `list`, like`['http://127.0.0.1:2380',]`

**return**:
nothing

##  etcd.Client.create_root

**syntax**:
`etcd.Client.create_root(password)`

Create root user in the cluster.

**arguments**:

-   `password`:
    The password of the root user.

**return**:
A `dict`, like`{"user":"root","roles":["root"]}`

##  etcd.Client.enable_auth

**syntax**:
`etcd.Client.enable_auth(root_password)`

Enable authorization.

**arguments**:

-   `password`:
    The password of the root user.

**return**:
nothing

##  etcd.Client.disable_auth

**syntax**:
`etcd.Client.disable_auth(root_password)`

Disable authorization.

**arguments**:

-   `password`:
    The password of the root user.

**return**:
nothing

##  etcd.Client.create_user

**syntax**:
`etcd.Client.create_user(name, password, root_password, roles=None)`

Create a user in the cluster.

**arguments**:

-   `name`:
    The name of the user.

-   `password`:
    The password of user.

-   `root_password`:
    The password of the root user.

-   `roles`:
    The roles that will be granted to the user.
    A `list`, like`['r1', 'r2']`. Defaults to `None`.

**return**:
A `dict`, like`{"user":"u1","roles":['r1']}`

##  etcd.Client.create_role

**syntax**:
`etcd.Client.create_role(name, root_password, permissions=None)`

Create a role in the cluster.

**arguments**:

-   `name`:
    The name of the role.

-   `root_password`:
    The password of the root user.

-   `permissions`:
    The permissions of the role.
    A `dict`, like`{'read': ['/*'], 'write': ['/*']}`.
    Defaults to `None`.

**return**:
A `dict`, like`{"role":"w_role","permissions":{"kv":{"read":["/*"],"write":["/*"]}}}`

##  etcd.Client.get_user

**syntax**:
`etcd.Client.get_user(name, root_password)`

Get the user information of the cluster.

**arguments**:

-   `name`:
    The name of the user.
    if `None`, return all users information.

-   `root_password`:
    The password of the root user.

**return**:
A `dict`, like
```python
{
  "user": "root",
  "roles": [
    {
      "role": "root",
      "permissions": {
        "kv": {
          "read": [
            "/*"
          ],
          "write": [
            "/*"
          ]
        }
      }
    }
  ]
}
```

##  etcd.Client.get_role

**syntax**:
`etcd.Client.get_role(name, root_password)`

Get the role information of the cluster.

**arguments**:

-   `name`:
    The name of the role.
    if `None`, return all roles information.

-   `root_password`:
    The password of the root user.

**return**:
A `dict`, like
```python
{
  "role": "w_role",
  "permissions": {
    "kv": {
      "read": [
        "/*"
      ],
      "write": [
        "/*"
      ]
    }
  }
}
```

##  etcd.Client.grant_user_roles

**syntax**:
`etcd.Client.grant_user_roles(name, root_password, roles)`

Grant roles to user.

**arguments**:

-   `name`:
    The name of the user.

-   `root_password`:
    The password of the root user.

-   `roles`:
    The roles that will be granted to the user.
    A `list`, like`['r1', 'r2']`.

**return**:
A `dict`, like`{u'user': u'u_test', u'roles': [u'r_test']}`

##  etcd.Client.revoke_user_roles

**syntax**:
`etcd.Client.revoke_user_roles(name, root_password, roles)`

Grant roles to user.

**arguments**:

-   `name`:
    The name of the user.

-   `root_password`:
    The password of the root user.

-   `roles`:
    The roles that will be revoked from the user.
    A `list`, like`['r1', 'r2']`.

**return**:
A `dict`, like`{u'user': u'u_test', u'roles': []}`

##  etcd.Client.grant_role_permissions

**syntax**:
`etcd.Client.grant_role_permissions(name, root_password, permissions)`

Grant permissions to the role.

**arguments**:

-   `name`:
    The name of the role.

-   `root_password`:
    The password of the root user.

-   `permissions`:
    The permissions that will be granted to the role.
    A `dict`, like`{'read': ['/*'], 'write': ['/*']}`.

**return**:
A `dict`, like`{u'role': u'r_test', u'permissions': {u'kv': {u'read': [u'/*'], u'write': []}}}`

##  etcd.Client.revoke_role_permissions

**syntax**:
`etcd.Client.revoke_role_permissions(name, root_password, permissions)`

Revoke permissions from the role.

**arguments**:

-   `name`:
    The name of the role.

-   `root_password`:
    The password of the root user.

-   `permissions`:
    The permissions that will be granted to the role.
    A `dict`, like`{'read': ['/*'], 'write': ['/*']}`.

**return**:
A `dict`, like`{u'role': u'r_test', u'permissions': {u'kv': {u'read': [], u'write': []}}}`

##  etcd.Client.delete_user

**syntax**:
`etcd.Client.delete_user(user_name, root_password)`

Delete the user of the cluster.

**arguments**:

-   `user_name`:
    The name of the user.

-   `root_password`:
    The password of the root user.

**return**:
nothing

##  etcd.Client.delete_role

**syntax**:
`etcd.Client.delete_role(role_name, root_password)`

Delete the role of the cluster.

**arguments**:

-   `role_name`:
    The name of the role.

-   `root_password`:
    The password of the root user.

**return**:
nothing

#   Author

Baohai Liu(刘保海) <baohai.liu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Baohai Liu(刘保海) <baohai.liu@baishancloud.com>
