<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Conf](#conf)
  - [file_path](#file_path)
  - [is_first_line](#is_first_line)
  - [get_level](#get_level)
  - [parse](#parse)
  - [level](#level)
- [Methods](#methods)
  - [collector.run](#collectorrun)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


#   Name

logcollector

Scan log files on local machine, collector all interested logs, and send
to somewhere for display.

#   Status

This library is considered production ready.

#   Synopsis

```python
from pykit.logcollector import collector

def send_log(log_entry):
    # send the log entry to database or other place.

def is_first_line(line):
    # return True if the line is the first line of a log,
    # otherwise return False.

def get_level(log_str):
    # return the level of the log.

def parse(log_str):
   # parse the log.

conf = {
    'front_error_log': {
        'file_path': 'path/to/log/file/xxx.error.log',
        'level': ['warn', 'error'],
        'is_first_line': is_first_line,
        'get_level': get_level,
        'parse': parse,
    },
}

kwargs = {
    'node_id': '123abc',
    'node_ip': '1.2.3.4',
    'send_log': send_log,
    'conf': conf,
}

collector.run(**argkv)
```

#   Description

We may want to see all error logs on all machines, so we need to collector
logs, and save it in somewhere. This module is used to collector logs on one
machine.

Normally, same error info will be loged repeatedly, we do not want
to save duplicated log info, so logs produced by same source file at
same line number in one second will be combined.

#   Conf

configuration for log files. It is a dict, the key is the log name, the value
is the configuration for the log.

## file_path

the path of the log file.

## is_first_line

is a callback function.
The argument to this function is a line in log file, if the line is the
first line of a log, then return `True`, otherwise return `False`.

## get_level

is a callback function.
The argument to this function is the complete log string, which may contains
multiple lines. It should return the level of the log, which is a string.

## parse

is a callback function.
The argument to this function is the complete log string, which may contains
multiple lines. It should return a dict contains following fields.

-   log_ts:
    the timestamp of this log, such as `1523936052`, is a integer.

-   level:
    the level of this log, such as 'info'.

-   source_file:
    the source file in which the log was produced.

-   line_number:
    the number of the line at which the log was produced.

## level

is a list, used to specify the interested log levels.

#   Methods

## collector.run

**syntax**:
`collector.run(**kwargs)`

Start to scan log files specified in conf.

**arguments**:

Following is all the valid keyword arguments.

-   `node_id`:
    the id of this machine. Required.

-   `node_ip`:
    the ip of this machine. Required.

-   `send_log`:
    a callback function, the argument to this function is the log entry,
    which contains following fields. Required.

    -   level:
        the level of the log.

    -   log_ts:
        the timestamp of the log.

    -   content:
        the full content of the log.

    -   log_name:
        the name of the log, specified in configuration.

    -   log_file:
        the file name of the log file.

    -   source_file:
        the source file in which the log was produced.

    -   line_number:
        the number of the line at which the log was produced.

    -   node_id:
        the id of the machine on which the log was produced.

    -   node_ip:
        the ip of the machine on which the log was produced.

    -   count:
        how many times this log repeated.

-   `conf`:
    the configuration of all log files to scan. Required.

**return**:
Not return

#   Author

Renzhi(任稚) <zhi.ren@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Renzhi(任稚) <zhi.ren@baishancloud.com>
