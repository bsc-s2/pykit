<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Class](#class)
  - [logutil.FixedWatchedFileHandler](#logutilfixedwatchedfilehandler)
- [Methods](#methods)
  - [logutil.add_std_handler](#logutiladd_std_handler)
  - [logutil.deprecate](#logutildeprecate)
  - [logutil.get_datefmt](#logutilget_datefmt)
  - [logutil.get_fmt](#logutilget_fmt)
  - [logutil.get_root_log_fn](#logutilget_root_log_fn)
  - [logutil.make_file_handler](#logutilmake_file_handler)
  - [logutil.make_formatter](#logutilmake_formatter)
  - [logutil.make_logger](#logutilmake_logger)
  - [logutil.stack_format](#logutilstack_format)
  - [logutil.stack_list](#logutilstack_list)
  - [logutil.stack_str](#logutilstack_str)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

logutil

#   Status

This library is considered production ready.

#   Synopsis

```python
# make a file logger in one line
logger = logutil.make_logger('/tmp', level='INFO', fmt='%(message)s',
                             datefmt="%H:%M:%S")
logger.info('foo')

logger.stack_str(fmt="{fn}:{ln} in {func}\n  {statement}", sep="\n")
# runpy.py:174 in _run_module_as_main
#   "__main__", fname, loader, pkg_name)
# runpy.py:72 in _run_code
#   exec code in run_globals
# ...
# test_logutil.py:82 in test_deprecate
#   logutil.deprecate()
#   'foo', fmt='{fn}:{ln} in {func}\n  {statement}', sep='\n')
```

#   Description

A collection of log utilities for logging.

#   Class

##  logutil.FixedWatchedFileHandler

**syntax**:
`logutil.FixedWatchedFileHandler(*args, **kwargs)`

Fix an issue with the original `logging.handlers.WatchedFileHandler` in python2:

Sometimes it raises an OSError when reading the log file stat after checking
existence of the log file.
Because the log file would be removed just after existence check and before
reading log file stat.

It has the same `__init__` arguments with
`logging.handlers.WatchedFileHandler`.

#   Methods

##  logutil.add_std_handler

**syntax**:
`logutil.add_std_handler(logger, stream=None, fmt=None, datefmt=None)`

It adds a `stdout` or `stderr` steam handler to the `logger`.

**arguments**:

-   `logger`:
    is an instance of `logging.Logger` to add handler to.

-   `stream`:
    specifies the stream, it could be:
    -   `sys.stdout` or a string `stdout`.
    -   `sys.stderr` or a string `stderr`.

-   `fmt`:
    is the log message format.
    It can be an alias name(like `default`) that can be used in
    `logutil.get_fmt()`.
    By default it is `default`: `[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s`.

-   `datefmt`:
    is the format for date.
    It can be an alias name(like `time`) that can be used in
    `logutil.get_datefmt()`.
    By default it is `None`.

**return**:
the `logger` argument.

##  logutil.deprecate

**syntax**:
`logutil.deprecate(msg=None, fmt=None, sep=None)`

Print a `deprecate` message with root logger, at warning level.
The printed message includes:

-   User defined message `msg`,
-   And calling stack of where this warning occurs.
    `<frame-n>` is where `logutil.deprecate` is called.

```
<msg> Deprecated: <frame-1> --- <frame-2> --- ... --- <frame-n>
```

The default frame format is `{fn}:{ln} in {func} {statement}`.
It can be changed with argument `fmt`.
Frame separator by default is ` --- `, and can be changed with argument `sep`.

For example, the following statement:

```
def foo():
    logutil.deprecate('should not be here.',
                      fmt="{fn}:{ln} in {func}\n  {statement}",
                      sep="\n"
                      )
```

Would produce a message:

```
Deprecated: should not be here.
runpy.py:174 in _run_module_as_main
  "__main__", fname, loader, pkg_name)
runpy.py:72 in _run_code
  exec code in run_globals
...
test_logutil.py:82 in test_deprecate
  logutil.deprecate()
  'foo', fmt='{fn}:{ln} in {func}\n  {statement}', sep='\n')
```

**arguments**:

-   `msg`:
    is description of the `deprecated` statement.
    It could be `None`.

-   `fmt`:
    is call stack frame format.
    By default it is `{fn}:{ln} in {func} {statement}`.

-   `sep`:
    is the separator string between each frame.
    By default it is ` --- `.
    Thus all frames are printed in a single line.

**return**:
Nothing.

##  logutil.get_datefmt

**syntax**:
`logutil.get_datefmt(datefmt)`

It translates a predefined datefmt alias to actual datefmt.
Predefined alias includes:

```
{
    'default':  None,       # use the system default datefmt
    'time':     '%H:%M:%S',
}
```

**arguments**:

-   `datefmt`:
    is the alias name.
    If no predefined alias name is found, it returns the passed in value of
    `datefmt`.

**return**:
translated `datefmt` or the original value of argument `datefmt`.

##  logutil.get_fmt

**syntax**:
`logutil.get_fmt(fmt)`

It translate a predefined fmt alias to actual fmt.
Predefined alias includes:

```
{
    'default':    '[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s',
    'time_level': "[%(asctime)s,%(levelname)s] %(message)s",
    'message':    '%(message)s',
}
```

**arguments**:

-   `fmt`:
    is the alias name.
    If no predefined alias name is found, it returns the passed in value of
    `fmt`.

**return**:
translated `fmt` or the original value of argument `fmt`.

##  logutil.get_root_log_fn

**syntax**:
`logutil.get_root_log_fn()`

The log file name suffix is `.out`.

-   `pyfn.out`: if program is started with `python pyfn.py`.
-   `__instant_command__.out`: if instance python command is called:
    `python -c "import logutil; print logutil.get_root_log_fn()`.
-   `__stdin__.out`: if python statement is passed in as stdin:
    `echo "from pykit import logutil; print logutil.get_root_log_fn()" | python`.

**return**:
log file name.

##  logutil.make_file_handler

**syntax**:
`logutil.make_file_handler(base_dir, log_fn, fmt=None, datefmt=None)`

It creates a rolling log file handler.

A rolling file can be removed at any time.
This handler checks file status everytime write log to it.
If file is changed(removed or moved), this handler automatically creates a new
log file.

**arguments**:

-   `base_dir`:
    specifies the dir of log file.

-   `log_fn`:
    specifies the log file name.

-   `fmt`:
    specifies log format.
    It can be an alias that can be used in `logutil.get_fmt()`, or `None` to
    used the `default` log format.

-   `datefmt`:
    specifies log date format.
    It can be an alias that can be used in `logutil.get_datefmt()`, or `None` to
    used the `default` date format.

**return**:
an instance of `logging.handlers.WatchedFileHandler`.

##  logutil.make_formatter

**syntax**:
`logutil.make_formatter(fmt=None, datefmt=None)`

It creates an `logging.Formatter` instance, with specified `fmt` and `datefmt`.

**arguments**:

-   `fmt`:
    specifies log format.
    It can be an alias that can be used in `logutil.get_fmt()`, or `None` to
    used the `default` log format.

-   `datefmt`:
    specifies log date format.
    It can be an alias that can be used in `logutil.get_datefmt()`, or `None` to
    used the `default` date format.

**return**:
an `logging.Formatter` instance.

##  logutil.make_logger

**syntax**:
`logutil.make_logger(base_dir, log_name=None, log_fn=None,
                     level=logging.DEBUG, fmt=None,
                     datefmt=None)`

It creates a logger with a rolling file hander and specified formats.

**arguments**:

-   `base_dir`:
    specifies the dir of log file.

-   `log_name`:
    is the name of the logger to create.
    `None` means the root logger.

-   `log_fn`:
    specifies the log file name.
    If it is `None`, use `logutil.get_root_log_fn` to make a log file name.

-   `level`:
    specifies log level.
    It could be int value such as `logging.DEBUG` or string such as `DEBUG`.

-   `fmt`:
    specifies log format.
    It can be an alias that can be used in `logutil.get_fmt()`, or `None` to
    used the `default` log format.

-   `datefmt`:
    specifies log date format.
    It can be an alias that can be used in `logutil.get_datefmt()`, or `None` to
    used the `default` date format.

**return**:
a `logging.Logger` instance.

##  logutil.stack_format

**syntax**:
`logutil.stack_format(stacks, fmt=None, sep=None)`

It formats stack made from `logutil.stack_list`.

With `fmt="{fn}:{ln} in {func}\n  {statement}"`
and `sep="\n"`, a formatted stack would be:

```
runpy.py:174 in _run_module_as_main
  "__main__", fname, loader, pkg_name)
runpy.py:72 in _run_code
  exec code in run_globals
...
test_logutil.py:82 in test_deprecate
  logutil.deprecate()
  'foo', fmt='{fn}:{ln} in {func}\n  {statement}', sep='\n')
```

**arguments**:

-   `stacks`:
    is stack from `logutil.stack_list`.

    ```
    [
        {
            'fn': ...
            'ln': ...
            'func': ...
            'statement': ...
        }
        ...
    ]
    ```

-   `fmt`:
    specifies the template to format a stack frame.
    By default it is: `{fn}:{ln} in {func} {statement}`.

-   `sep`:
    specifies the separator string between each stack frame.
    By default it is ` --- `.
    Thus all frames are in the same line.

**return**:
a string repesenting a calling stack.

##  logutil.stack_list

**syntax**:
`logutil.stack_list(offset=0)`

It returns the calling stack from where it is called.

**arguments**:

-   `offset`:
    remove the lowest `offset` frames.

**return**:
list of:

```
{
    'fn': ...
    'ln': ...
    'func': ...
    'statement': ...
}
```


##  logutil.stack_str

**syntax**:
`logutil.stack_str(offset=0, fmt=None, sep=None)`

It creates a string representing calling stack from where this function is
called.

**arguments**:

-   `offset=0`:
    remove the lowest `offset` frames.
    Because usually one does not need the frame of the `logutil.stack_str`
    line.

-   `fmt`: is same as `logutil.stack_format`.
-   `sep`: is same as `logutil.stack_format`.

**return**:
a string repesenting a calling stack.


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
