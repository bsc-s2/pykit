<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [daemonize.daemonize_cli](#daemonizedaemonize_cli)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

daemonize.py

Create daemon process.


#   Status

This library is considered production ready.

#   Synopsis

`foo.py`:

```python
# foo.py
import time
from pykit import daemonize
def run():
    for i in range(100):
        print i
        time.sleep(1)

if __name__ == '__main__':
    # there is at most only one of several processes with the same pid path
    # that can run.
    daemonize.daemonize_cli(run, '/var/run/pid')
```

To control foo.py from command line:

```
python2 foo.py start
python2 foo.py stop
python2 foo.py restart
```

#   Description

Help to create daemon process.
It supplies a command line interface API to start/stop/restart a daemon.

`daemonize` identifies a daemon by the `pid` file.
Thus two processes those are set up with the same `pid` file
can not run at the same time.

#   Methods

## daemonize.daemonize_cli

**syntax**:
`daemonize.daemonize_cli(callable, pid_path, close_fds=False)`

Read command line arguments and then start, stop or restart a daemon process.

**arguments**:

-   `callable`:
    a callable object such as a `function` or `lambda` to run after the daemon
    process is created.

-   `pid_path`:
    abosolute path of `pid` file.
    It is used to identify a daemon process.
    Thus two processes those are with the same `pid` file can not run at the
    same time.

-   `close_fds`:
    If it is `True`, besides `stdin`, `stdout` and `stderr`, all other file descriptors
    will also be closed.

**return**:
None

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
