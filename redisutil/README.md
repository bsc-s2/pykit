<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Synopsis](#synopsis)
- [Exceptions](#exceptions)
  - [redisutil.RedisProxyError](#redisutilredisproxyerror)
  - [redisutil.SendRequestError](#redisutilsendrequesterror)
  - [redisutil.KeyNotFoundError](#redisutilkeynotfounderror)
  - [redisutil.ServerResponseError](#redisutilserverresponseerror)
- [Methods](#methods)
  - [redisutil.get_client](#redisutilget_client)
  - [redisutil.wait_serve](#redisutilwait_serve)
- [Classes](#classes)
  - [redisutil.RedisChannel](#redisutilredischannel)
    - [RedisChannel.send_msg](#redischannelsend_msg)
    - [RedisChannel.recv_msg](#redischannelrecv_msg)
    - [RedisChannel.brecv_msg](#redischannelbrecv_msg)
    - [RedisChannel.recv_last_msg](#redischannelrecv_last_msg)
    - [RedisChannel.brecv_last_msg](#redischannelbrecv_last_msg)
    - [RedisChannel.peek_msg](#redischannelpeek_msg)
    - [RedisChannel.rpeek_msg](#redischannelrpeek_msg)
    - [RedisChannel.list_channel](#redischannellist_channel)
  - [redisutil.RedisProxyClient](#redisutilredisproxyclient)
    - [RedisProxyClient.get](#redisproxyclientget)
    - [RedisProxyClient.set](#redisproxyclientset)
    - [RedisProxyClient.hget](#redisproxyclienthget)
    - [RedisProxyClient.hset](#redisproxyclienthset)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

redisutil

#   Status

This library is considered production ready.

#   Description

For using redis more easily.

#   Synopsis

```python
# Using redis as a duplex cross process communication channel pool.

# client and server with the same channel name "/foo" is a pair
c = redisutil.RedisChannel(6379, '/foo', 'client')
s = redisutil.RedisChannel(6379, '/foo', 'server')

c.send_msg('c2s')
s.send_msg('s2c')

# list channels
print c.list_channel('/') # ["/foo"]
print s.recv_msg()        # c2s
print c.recv_msg()        # s2c

```

```python
cli = redisutil.RedisProxyClient([('127.0.0.1', 2222), ('192.168.0.100', 222)])

cli.set('k1', 'v1', retry=1)
cli.set('k2', 'v2', expire=1000) # msec

print cli.get('k1', retry=2)
# out: 'v1'

print cli.get('k2')
# out: 'v2'

time.sleep(1)
cli.get('k2')
# raise a 'redisutil.KeyNotFoundError' because it is timeout

cli.hset('hashname1', 'k3', 'v3')
cli.hset('hashname2', 'k4', 'v4', expire=1000)

print cli.hget('hashname1', 'k3')
# out: 'v3'

print cli.hget('hashname2', 'k4')
# out: 'v4'

time.sleep(1)
cli.hget('hashname2', 'k4')
# raise a 'redisutil.KeyNotFoundError' because it is timeout

```

#   Exceptions

##  redisutil.RedisProxyError

**syntax**:
`redisutil.RedisProxyError`

The base class of other exceptions of `RedisProxyClient`.
It is a subclass of `Exception`.

##  redisutil.SendRequestError

**syntax**:
`redisutil.SendRequestError`

It is a subclass of `redisutil.RedisProxyError`.
Raise if failed to send request to redis proxy server.

##  redisutil.KeyNotFoundError

**syntax**:
`redisutil.KeyNotFoundError`

It is a subclass of `redisutil.RedisProxyError`.
Raise if key not found (redis proxy server return a `404`).

##  redisutil.ServerResponseError

**syntax**:
`redisutil.ServerResponseError`

It is a subclass of `redisutil.RedisProxyError`.
Raise if http-status not in `(200, 404)` return from redis proxy server.

#   Methods

##  redisutil.get_client

**syntax**:
`redisutil.get_client(ip_port)`

Return a process-wise singleton redis client, which is an instance of `redis.StrictRedis`.

Redis client returned is shared across the entire process and will not be
re-created.

It is also safe to use if a process fork and inherited opened socket file-descriptors.

**arguments**:

-   `ip_port`: could be a port number in `int` or `long` to get or create a
    client connecting to localhost.

    It can also be tuple of `(ip, port)`.

**return**:
an instance of `redis.StrictRedis`.


##  redisutil.wait_serve

**syntax**:
`redisutil.wait_serve(ip_port, timeout=5)`

Wait for at most `timeout` seconds until redis start serving request.
It is useful when start a redis server.

**arguments**:

-   `ip_port`:
    tuple of `(ip, port)` or a single int/long number as port.

-   `timeout`:
    specifies max waiting time, in seconds.

**return**:
Nothing

**raise**:

-   `redis.ConnectionError`:
    if redis does not respond in `timeout` seconds.

#   Classes

##  redisutil.RedisChannel

**syntax**:
`redisutil.RedisChannel(ip_port, channel, peer, timeout=None)`

Create a redis list based channel for cross process communication.

See [redis-list-command](https://redis.io/commands#list).

Initializing this class does **NOT** create a socket connecting to redis or
create any data in redis.

A channel support duplex communication.
Thus in redis it creates two lists for each channel for two way communication:
`<channel>/client` and `<channel>/server`.

Client side uses `<channel>/client` to send message.
Server side uses `<channel>/server` to send message.

A client should initialize `RedisChannel` with argument `peer` set to `client`.
A server should initialize `RedisChannel` with argument `peer` set to `server`.

**arguments**:

-   `ip_port`:
    tuple of `(ip, port)` or a single int/long number as port.

-   `channel`:
    specifies the name of the channel to create.

    A channel should be in URI form, starting with `/`, such as: `/asyncworker/image-process`

    `channel` can also be a tuple of string:
    `('asyncworker', 'image-process')` will be converted to `/asyncworker/image-process`.

-   `peer`:
    specifies this instance is a client or a server.
    It can be `"client"` or `"server"`.

-   `timeout`:
    the expire time of the channel, in second.
    If it is `None`, the channel exists until being cleaned.

**return**:
an instance of `RedisChannel`.

###  RedisChannel.send_msg

**syntax**:
`RedisChannel.send_msg(data)`

Send data. `data` is json-encoded in redis list.

**arguments**:

-   `data`:
    any data type that can be json encoded.

**return**:
Nothing

###  RedisChannel.recv_msg

**syntax**:
`RedisChannel.recv_msg()`

Receive one message.
If there is no message in this channel, it returns `None`.

**return**:
data that is loaded from json. Or `None` if there is no message in channel.

###  RedisChannel.brecv_msg

**syntax**:
`RedisChannel.brecv_msg(timeout=0)`

Block to receive one message.
If there is no message in this channel,
then block for `timeout` seconds or until
a value was pushed to the channel.

**arguments**:

-   `timeout`:
    seconds of the block time.
    If it is `0`, then block until a message is available.

**return**:
data that is loaded from json. Or `None` if timeout.

###  RedisChannel.recv_last_msg

**syntax**:
`RedisChannel.recv_last_msg()`

Similar to `RedisChannel.recv_msg` except it returns only the last message it
sees and removes all previous messages from this channel.

**return**:
data that is loaded from json. Or `None` if there is no message in channel.

###  RedisChannel.brecv_last_msg

**syntax**:
`RedisChannel.brecv_last_msg(timeout=0)`

Similar to `RedisChannel.recv_last_msg` except it blocks for `timeout`
seconds if the channel is empty.

**arguments**:

-   `timeout`:
    seconds of the block time.
    If it is `0`, then block until a message is available.

**return**:
data that is loaded from json. Or `None` if timeout.

###  RedisChannel.peek_msg

**syntax**:
`RedisChannel.peek_msg()`

Similar to `RedisChannel.recv_msg` except it does not remove the message it
returned.

**return**:
data that is loaded from json. Or `None` if there is no message in channel.

###  RedisChannel.rpeek_msg

**syntax**:
`RedisChannel.rpeek_msg()`

Similar to `RedisChannel.peek_msg`
except it gets message from the tail of the channel.

**return**:
JSON decoded message. Or `None` if there is no message in channel.

###  RedisChannel.list_channel

**syntax**:
`RedisChannel.list_channel(prefix)`

List all channel names those start with `prefix`.

**arguments**:

-   `prefix`:
    specifies what channel to list.

    `prefix` must starts with '/', ends with '/'.

**return**:
a list of channel names.

##  redisutil.RedisProxyClient

**syntax**:
`redisutil.RedisProxyClient(hosts, nwr=None, ak_sk=None, timeout=None)`

A client for redis proxy server.

**arguments**:

-   `hosts`:
    a `tuple` each element is a `(ip, port)`, retry with next addr while failed to use prev one.

-   `nwr`:
    `tuple` of `(n, w, r)`, count of replicas, count of write, count of read.
    If it is `None`, `config.rp_cli_nwr` is used.

-   `ak_sk`:
    `tuple` of `(access_key, secret_key)` to sign the request.
    If it is `None`, `config.rp_cli_ak_sk` is used.

-   `timeout`:
    timeout of connecting redis proxy server in seconds. Defaults to `None`.

###  RedisProxyClient.get

**syntax**:
`RedisProxyClient.get(key, retry=0)`

Get the value with `key`.
Raise a `redisutil.KeyNotFoundError` if the key doesn’t exist.

**arguments**:

-   `key`:
    specifies the key to redis.

-   `retry`:
    try to send request for another N times while failed to send request.
    By default, it is `0`.

**return**:
the value at `key`.

###  RedisProxyClient.set

**syntax**:
`RedisProxyClient.set(key, val, expire=None, retry=0)`

Set the value at `key` to `val`.

**arguments**:

-   `key`:
    specifies the key to redis.

-   `val`:
    specifies the value to redis.

-   `expire`:
    the expire time on `key` in msec. Defaults to `None`.

-   `retry`:
    try to send request for another N times while failed to send request.
    By default, it is `0`.

**return**:
nothing

###  RedisProxyClient.hget

**syntax**:
`RedisProxyClient.hget(hashname, hashkey, retry=0)`

Return the value of `haskkey` within the `haskname`.
Raise a `redisutil.KeyNotFoundError` if it doesn’t exist.

**arguments**:

-   `hashname`:
    specifies the hash name to redis.

-   `hashkey`:
    specifies the hash key to redis.

-   `retry`:
    try to send request for another N times while failed to send request.
    By default, it is `0`.

**return**:
the value of `hashkey` within the `hashname`.

###  RedisProxyClient.hset

**syntax**:
`RedisProxyClient.hset(hashname, hashkey, val, expire=None, retry=0)`

Set `hashkey` to `val` within `hashname`.

**arguments**:

-   `hashname`:
    specifies the hash name to redis.

-   `hashkey`:
    specifies the hash key to redis.

-   `val`:
    specifies the value to redis.

-   `expire`:
    the expire time on `hashkey` within `hashname` in msec. Defaults to `None`.

-   `retry`:
    try to send request for another N times while failed to send request.
    By default, it is `0`.

**return**:
nothing

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
