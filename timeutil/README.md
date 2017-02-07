<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [timeutil.parse](#timeutilparse)
  - [timeutil.format](#timeutilformat)
  - [timeutil.format_ts](#timeutilformatts)
  - [timeutil.utc_datetime_to_ts](#timeutilutcdatetime_to_ts)
  - [timeutil.ts_to_datetime](#timeutilts_to_datetime)
  - [timeutil.ts](#timeutilts)
  - [timeutil.ms](#timeutilms)
  - [timeutil.us](#timeutilus)
  - [timeutil.ms_to_ts](#timeutilms_to_ts)
  - [timeutil.us_to_ts](#timeutilus_to_ts)

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

print timeutil.ts(), timeutil.ms(), timeutil.us()

```

# Description

Utility functions for time related operation.

#   Methods

## timeutil.parse

**syntax**:

`timeutil.parse(time_str, fmt_key)`

parse time string to datetime instance.

**arguments**:

-   `time_str`:
    time_str format, please refer to timeutil.formats, for example:
    'Tue, 24 Jan 2017 07:51:59 UTC', '2017-01-24T07:51:59.000Z'

-   `fmt_key`
    specify time string format type,
    value: default, iso, utc, archive, compact, daily, mysql, nginxaccesslog, nginxerrorlog

**return**:
    datetime instance

##  timeutil.format

**syntax**:

`timeutil.format(dt, fmt_key)`

convert datetime instance to specify format time string

**arguments**:

-   `dt`:
    datetime instance

-   `fmt_key`:
    specify time string format type,
    value: default, iso, utc, archive, compact, daily, mysql, nginxaccesslog, nginxerrorlog

**return**:
    specify format time string

##  timeutil.format_ts

**syntax**:

`timeutil.format_ts(ts, fmt_key)`

convert timestamp to specify format time string

**arguments**:

-   `ts`:
    timestamp in second

-   `fmt_key`:
    specify time string format type,
    value: default, iso, utc, archive, compact, daily, mysql, nginxaccesslog, nginxerrorlog

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

# Author

cc (陈闯) <chuang.chen@baishancloud.com>

# Copyright and License

The MIT License (MIT)

Copyright (c) 2017 cc (陈闯) <chuang.chen@baishancloud.com>
