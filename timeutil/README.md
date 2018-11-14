<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [timeutil.parse](#timeutilparse)
  - [timeutil.parse_to_ts](#timeutilparse_to_ts)
  - [timeutil.format](#timeutilformat)
  - [timeutil.format_ts](#timeutilformat_ts)
  - [timeutil.utc_datetime_to_ts](#timeutilutc_datetime_to_ts)
  - [timeutil.datetime_to_ts](#timeutildatetime_to_ts)
  - [timeutil.ts_to_datetime](#timeutilts_to_datetime)
  - [timeutil.ts](#timeutilts)
  - [timeutil.ms](#timeutilms)
  - [timeutil.us](#timeutilus)
  - [timeutil.ns](#timeutilns)
  - [timeutil.ms_to_ts](#timeutilms_to_ts)
  - [timeutil.us_to_ts](#timeutilus_to_ts)
  - [timeutil.ns_to_ts](#timeutilns_to_ts)
  - [timeutil.to_sec](#timeutilto_sec)
  - [timeutil.is_timestamp](#timeutilis_timestamp)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Name

timeutil

Support specify time format output and get current ts, ms, us api etc

# Status

This library is considered production ready.

# Synopsis

```
from pykit import timeutil

dt = timeutil.parse('2017-01-24T07:51:59.000Z', 'iso')

time_str = timeutil.format(dt, 'utc')

ts = timeutil.utc_datetime_to_ts(dt)

print ts, time_str

print timeutil.ts(), timeutil.ms(), timeutil.us(), timeutil.ns()

```

# Description

Utility functions for time related operation.

#   Methods

## timeutil.parse

**syntax**:

`timeutil.parse(time_str, fmt_key, timezone=None)`

parse time string to datetime instance.

**arguments**:

-   `time_str`:
    time in string. Please refer to timeutil.formats, for example:
    `'Tue, 24 Jan 2017 07:51:59 UTC'`, `'2017-01-24T07:51:59.000Z'`.

-   `fmt_key`:
    specify time string format.
    It can be a named format alias, or format string:

    ```
    'default':        '%a, %d %b %Y %H:%M:%S UTC',
    'iso':            '%Y-%m-%dT%H:%M:%S.000Z',
    'utc':            '%a, %d %b %Y %H:%M:%S UTC',
    'archive':        '%Y%m%d-%H',
    'compact':        '%Y%m%d-%H%M%S',
    'daily':          '%Y-%m-%d',
    'mysql':          '%Y-%m-%d %H:%M:%S',
    'nginxaccesslog': "%d/%b/%Y:%H:%M:%S",
    'nginxerrorlog':  "%Y/%m/%d %H:%M:%S",
    ```

    Thus `parse(tm, "default")` is same as `parse(tm, "%a, %d %b %Y %H:%M:%S UTC")`.

-   `timezone`:
    specify a timezone to get an aware datetime object. It is a string,
    such as 'Asia/Shanghai'.

**return**:
datetime instance


##  timeutil.parse_to_ts

**syntax**:
`timeutil.parse_to_ts(time_str, fmt_key)`

Similar to `parse` but returns a timestamp in second instead of a `datetime`
instance.

**arguments**:

-   `time_str`:
    time in string.

-   `fmt_key`:
    specify time string format.

**return**:
an int timestamp in second.


##  timeutil.format

**syntax**:

`timeutil.format(dt, fmt_key)`

convert datetime instance to specify format time string

**arguments**:

-   `dt`:
    datetime instance

-   `fmt_key`:
    specify time string format.
    It can be a named format alias, or format string.

**return**:
    specify format time string

##  timeutil.format_ts

**syntax**:

`timeutil.format_ts(ts, fmt_key, utc=True)`

convert timestamp to specify format time string

**arguments**:

-   `ts`:
    timestamp in second

-   `fmt_key`:
    specify time string format.
    It can be a named format alias, or format string.

-   `utc`:
    set to `True` to get utc time, set to `False` to get local time.

**return**:
    specify format time string

##  timeutil.utc_datetime_to_ts

**syntax**:

`utc_datetime_to_ts(dt)`

convert datetime instance to timestamp in second

**arguments**:

-   `dt`:
    datetime instance

**return**:
    timestamp in second

##  timeutil.datetime_to_ts

**syntax**:

`datetime_to_ts(dt)`

convert naive or aware datetime instance to timestamp in second

**arguments**:

-   `dt`:
    datetime instance, if it does not contain timezone info, we
    assume it has a local timezone.

**return**:
    timestamp in second

##  timeutil.ts_to_datetime

**syntax**:

`ts_to_datetime(ts)`

convert timestamp in second to datetime instance

**arguments**:

-   `ts`:
    timestamp in second

**return**:
    datetime instance

##  timeutil.ts

**syntax**:

`ts()`

get now timestamp in second

**return**:
    timestamp in second


##  timeutil.ms

**syntax**:

`ms()`

get now timestamp in millisecond

**return**:
    timestamp in millisecond

##  timeutil.us

**syntax**:

`us()`

get now timestamp in microsecond

**return**:
    timestamp in microsecond

##  timeutil.ns

**syntax**:

`ns()`

get now timestamp in nanosecond

**return**:
    timestamp in nanosecond

##  timeutil.ms_to_ts

**syntax**:

`ms_to_ts(ms)`

convert timestamp from millisecond to second

**arguments**:

-   `ms`:
    timestamp in millisecond

**return**:
    timestamp in second

##  timeutil.us_to_ts

**syntax**:

`us_to_ts(us)`

convert timestamp from microsecond to second

**arguments**:

-   `us`:
    timestamp in microsecond

**return**:
    timestamp in second

##  timeutil.ns_to_ts

**syntax**:

`ns_to_ts(ns)`

convert timestamp from nanosecond to second

**arguments**:

-   `ns`:
    timestamp in nanosecond

**return**:
    timestamp in second

##  timeutil.to_sec

**syntax**:
`timeutil.to_sec(val)`

Convert timestamp in second, ms, us or ns to second.
If `val` is not a valid timestamp, it raises `ValueError`.

**arguments**:

-   `val`: timestamp in int, long, float or string.
    It can be a timestamp in second, millisecond(10e-3), microsecond(10e-6) or
    nanosecond(10e-9).

**return**:
timestamp in second

##  timeutil.is_timestamp

**syntax**:
`timeutil.is_timestamp(ts, unit=None)`

It check if `ts` is a valid timestamp, in string or number.

**arguments**:

-   `ts`:
    is string or number.

-   `unit`:
    specifies what the unit `ts` is in:

    -   `s`:     second
    -   `ms`:    millisecond `10^-3`
    -   `us`:    microsecond `10^-6`
    -   `ns`:    nanosecond  `10^-9`

    -   `None`:  any of above

**return**:
`True` or `False`.

# Author

cc (陈闯) <chuang.chen@baishancloud.com>

# Copyright and License

The MIT License (MIT)

Copyright (c) 2017 cc (陈闯) <chuang.chen@baishancloud.com>
