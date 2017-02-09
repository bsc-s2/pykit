<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Exceptions](#exceptions)
  - [portlock.PortlockError](#portlockportlockerror)
  - [portlock.PortlockTimeout](#portlockportlocktimeout)
- [Classes](#classes)
  - [portlock.Portlock](#portlockportlock)
- [Methods](#methods)
  - [Portlock.acquire](#portlockacquire)
  - [Portlock.release](#portlockrelease)
  - [Portlock.has_locked](#portlockhas_locked)
  - [with Portlock](#with-portlock)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


# Name

portlock

# Status

This library is considered stable.

# Description

`Portlock` is a cross-process lock that is implemented with `tcp` port binding.
Since no two processes could bind on a same TCP port.

`Portlock` tries to bind **3** ports on loopback ip `127.0.0.1`.
If a `Portlock` instance succeeds on binding **2** ports out of 3,
it is considered this instance has acquired the lock.


# Exceptions


## portlock.PortlockError

**syntax**:
`portlock.PortlockError`

Super class of all Portlock exceptions.


## portlock.PortlockTimeout

**syntax**:
`portlock.PortlockTimeout`

Timeout when waiting to acquire the lock.


# Classes


## portlock.Portlock

**syntax**:
`portlock.Portlock(key, timeout=1, sleep_time=None)`

A lock instance.

Portlock is thread safe.
It is OK to create just one lock in a process for all threads.

**arguments**:

-   `key`:
    is a string as lock key.
    `key` will be hashed to a certain port

-   `timeout`:
    is the max time in second to wait to acquire the lock.

    If `acquire()` exceeds `timeout`,
    it raises an `portlock.PortlockTimeout` exception.

-   `sleep_time`:
    is the time in second between every two attempts to bind a port.


# Methods


## Portlock.acquire

**syntax**:
`Portlock.acquire()`

It tries to acquire the lock before `timeout`.

**return**:
nothing


## Portlock.release

**syntax**:
`Portlock.release()`

It releases the lock it holds, or does nothing if it does not hold the lock.

**return**:
nothing


## Portlock.has_locked

**syntax**:
`Portlock.has_locked()`

It checks if this instances has the lock.

**return**:
`True` if it has the lock.


## with Portlock

**syntax**:
`with Portlock(key):`

`Portlock` supports `with` statement.

When entering a `with` statement of `Portlock` instance it invokes `acquire()`
automatically.

And when leaving `with` block, `release()` will be called to release the lock.


# Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

# Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
