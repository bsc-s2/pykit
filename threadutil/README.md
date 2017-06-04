<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
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

## raise_in_thread

Raises an exception in the given thread.
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

#   Author

Shuoqing Ding (丁硕青) <dsq704136@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Shuoqing Ding (丁硕青) <dsq704136@gmail.com>
