<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Background](#background)
- [What does this module do](#what-does-this-module-do)
- [Duplicated logs](#duplicated-logs)
- [Design](#design)
  - [Scanner](#scanner)
  - [Cache flusher](#cache-flusher)
  - [Sender](#sender)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Background

How can we known whether there are error logs on some machine,
we can log in to each machine and grep each log file, but it is
not an easy way.

So we collect all interested logs(maybe error and warning logs),
and keep them at some place(maybe database). Then we do not need
to log in to each machine and grep each log.

#   What does this module do

This module is used to scan all log files on a machine, for each
interested log, it call the callback function, which should send
the log to somewhere.

#   Duplicated logs

Usually, there are a lot of duplicated logs in a log file, they
are produced by same source file at same line number.

It does not make sense to keep all those duplicated logs, so if
a log repeated many times in a second, we combine them to one
log entry. No matter how many times a log repeated, only one log
entry will be kept in every second.

#   Design

This module consists of three main sub modules.

## Scanner

For each log file, we start a new thread to scan the file.

The scanner scan the log file line by line. For each line, it call
the callback function `is_first_line` to check if this line is the
first line of a log and thus to separate each log.

For each log, if call the callback function `parse` to parse the log,
and get the basic info of the log, includes timestamp, level, source
file, line number. Then from these information, it build a log entry.

In order to combine duplicated logs, the scanner put each log entry
into `log_cache` which is a dict. It looks like:

``` python
log_cache = {
    1524126615: {
        'source_file_a': {
            123: { # 123 is the line number
                'log_ts': 1524126615,
                'level': 'info',
                'source_file': 'source_file_a',
                'content': 'the full content of the log',
                ...
                'count': 3,
            },
            ...
        },
        ...
    },
    1524126616: {
        ...
    },
    ...
}
```

So for the same timestamp, same source file, same line number, there
is only one log entry, and we use `count` to indicate how many times
this log has repeated.

## Cache flusher

The cache flusher look at the `log_cache` periodically, pick log entry
out of `log_cache`, and put it into a queue. It will sort the log entries
by timestamp, and it only pick out log entries with relatively older
timestamp, because, they can not be combined with following log entries.

## Sender

The Sender just get log entry one by one from the queue, and call the
callback function `send_log`.
