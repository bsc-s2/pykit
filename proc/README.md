<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Synopsis](#synopsis)
- [Exceptions](#exceptions)
  - [proc.ProcError](#procprocerror)
- [Methods](#methods)
  - [proc.command](#proccommand)
  - [proc.command_ex](#proccommand_ex)
  - [proc.shell_script](#procshell_script)
  - [proc.start_process](#procstart_process)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


#   Name

proc

#   Status

This library is considered production ready.

#   Description

Utility to create sub process.

#   Synopsis

```python
from pykit import proc

# execute a shell script

returncode, out, err = proc.shell_script('ls / | grep bin')
print returncode
print out
# output:
# > 0
# > bin
# > sbin

# Or run a command directly.
# Unlike the above snippet, following statement does not start an sh process.

returncode, out, err = proc.command('ls', 'a*', cwd='/usr/local')
```

```python
# a.py
import sys

with open('foo', 'w') as f:
    f.write(str(sys.argv))

# b.py
import time
from pykit import proc

proc.start_daemon('python', './a.py', 'test')
time.sleep(1)
try:
    with open('foo', 'r') as f:
        print repr(f.read())
except Exception as e:
    print repr(e)
```

#   Exceptions

##  proc.ProcError

**syntax**:
`proc.ProcError(returncode, out, err, cmd, arguments, options)`

It is raised if a sub process return code is not `0`.
Besides `ProcError.args`, extended from super class `Exception`, it has 6
other attributes.

**attributes**:

-   `ProcError.returncode`:   process exit code.
-   `ProcError.out`:          stdout in one string.
-   `ProcError.err`:          stderr in one string.
-   `ProcError.cmd`:          the command a process `exec()`.
-   `ProcError.arguments`:    tuple of command arguments.
-   `ProcError.options`:      other options passed to this process. Such as `close_fds`, `cwd` etc.

#   Methods

##  proc.command

**syntax**:
`proc.command(cmd, *arguments, **options)`

Run a `command` with arguments `arguments` in a subprocess.
It blocks until sub process exit.

**arguments**:

-   `cmd`:
    The path of executable to run.

-   `arguments`:
    is tuple or list of arguments passed to `cmd`.

-   `options`:
    is a dictionary or additional options:

    -   `close_fds`: specifies whether to close all open file descriptor when
        `fork()`. By default it is `True`.

    -   `cwd`:  specifies working dir of the sub process. By default it is
        `None`, which means does not change current working dir.

    -   `env`:  is a dictionary to pass environment variables to sub process.

    -   `stdin`: is a string used as stdin for sub process. By default it is
        `None`.

**return**:
a 3 element tuple that contains:

-   `returncode`:   sub process exit code in `int`.
-   `out`:  sub process stdout in a single string.
-   `err`:  sub process stderr in a single string.

##  proc.command_ex

**syntax**:
`proc.command_ex(cmd, *arguments, **options)`

It is the same as `proc.command` except that if sub process exit code is not
0, it raises exception `proc.ProcError`.

See `proc.ProcError`.

**return**:
a 3 element tuple of `returncode`, `out` and `err`, or raise exception
`proc.ProcError`.

##  proc.shell_script

**syntax**:
`proc.shell_script(script_str, **options)`

It is just a shortcut of:
```
options['stdin'] = script_str
return command('sh', **options)
```

##  proc.start_process

**syntax**:
`proc.start_process(cmd, target, env, *args)`

Create a child process and replace it with `cmd`.
Besides `stdin`, `stdout` and `stderr`, all file
descriptors from parent process will be closed in
the child process. The parent process waits for
the child process until it is completed.

**arguments**:

-   `cmd`:
    The path of executable to run.
    Such as `sh`, `bash`, `python`.

-   `target`:
    The path of the script.

-   `env`:
    It is a dictionary to pass environment variables
    to the child process.

-   `*args`:
    Type is `tuple` or `list`.
    The arguments passed to the script.
    Type of every element must be `str`.

**return**:
nothing

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
