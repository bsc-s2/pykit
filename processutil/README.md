<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Contents

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [processutil.start_exec_process](#processutilstart_exec_process)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

processutil

#   Status

This library is considered production ready.

#   Synopsis

```python
# a.py
import sys

with open('foo', 'w') as f:
    f.write(str(sys.argv))

# b.py
import time
from pykit import processutil

processutil.start_exec_process('python', './a.py', 'test')
time.sleep(1)
try:
    with open('foo', 'r') as f:
        print repr(f.read())
except Exception as e:
    print repr(e)
```

```python
# a.sh
echo '123456' > 'foo'

# b.py
import time
from pykit import processutil

processutil.start_exec_process('sh', './a.sh')
time.sleep(1)
try:
    with open('foo', 'r') as f:
        print repr(f.read())
except Exception as e:
    print repr(e)
```

#   Description

It provides with several process operation functions.

# Methods

##  processutil.start_exec_process

**syntax**:
`processutil.start_exec_process(cmd, target, *args):`

Create a deamonize process and replace it with `target`.
Raise a `OSError` if failed to create daemonize process.

**arguments**:

-   `cmd`:
    The path of executable to run.
    Such as `sh`, `bash`, `python`.

-   `target`:
    The path of the script.

-   `*args`:
    The arguments passed to the script. Type is `tuple` or `list`.

**return**:
nothing

#   Author

Baohai Liu (刘保海) <baohai.liu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Baohai Liu (刘保海) <baohai.liu@baishancloud.com>
