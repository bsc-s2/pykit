<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [start_thread](#start_thread)
  - [start_daemon_thread](#start_daemon_thread)
  - [raise_in_thread](#raise_in_thread)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

threadutil

#   Status

This library is considered production ready.

#   Synopsis

```python
import threading
import time

from pykit import threadutil

def x():
    while True:
        # some work
        time.sleep(0.1)

t = threading.Thread(target=x)
t.start()

threadutil.threadutil.raise_in_thread(t, SystemExit)
```

#   Description

A collection of helper function for managing python threads easily.


# Methods

## start_thread

Create and start a thread with the given parameters.

**Syntax**

```
t = threadutil.start_thread(work, name='my_thread', args=(10, ), kwargs={'x': 2}, daemon=True)
```

**Arguments**

- `target`:
    The callable object to run.

- `name`:
    The thread name. By default, a unique name is constructed of the form "Thread-N" where N is a small decimal number.

- `args`:
    The argument tuple for the target invocation. Defaults to `()`.

- `kwargs`:
    A dictionary of keyword arguments for the target invocation. Defaults to `{}`.

- `daemon`:
    Whether to create a daemon thread.

**Returns**

The created thread object.

## start_daemon_thread

Create and start a daemon thread. See `start_thread` method for more detail.


## raise_in_thread

Asynchronously Raises an exception in the given thread.
It is useful when you want to terminate some threads from the main thread.

Please note that the exception will be raised only when executing python bytecode.
If your thread calls a native/built-in blocking function, the exception will be
raised only when execution returns to the python code.

**Syntax**

```
threadutil.raise_in_thread(thread, exception)
```

**Arguments**

- `thread`:
    A `threading.Thread` instance who we will raise the exception.

- `exception`:
    A exception class that will be raised in the thread.

**Returns**

`None`

**Raises**

- `InvalidThreadIdError` if the given thread is not alive or found.
- `TypeError` or `ValueError` if any input is illegal.
- `AsyncRaiseError` for other unexpected errors.

#   Author

Shuoqing Ding (丁硕青) <dsq704136@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Shuoqing Ding (丁硕青) <dsq704136@gmail.com>
