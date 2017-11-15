<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Classes](#classes)
  - [ratelimiter.RateLimiter](#ratelimiterratelimiter)
    - [RateLimiter.consume](#ratelimiterconsume)
    - [RateLimiter.wait_available](#ratelimiterwait_available)
    - [RateLimiter.set_permits](#ratelimiterset_permits)
    - [RateLimiter.get_stored](#ratelimiterget_stored)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

ratelimiter

#   Status

This library is considered not test well.

#   Synopsis
This module has two usages.

One is pre consume and get left capacity, another is request and wait mode.
Here is the example:

```python
import time

from pykit import ratelimiter

# pre consume and get left capacity
r = throttle.RateLimiter(100, 2)
r.consume(1000)
if r.get_stored() < 0:
   print "not enough permits"
else:
   print "can assign permits is %s" % r.get_stored()

# request and wait
r = throttle.RateLimiter(100, 2)
# this will request 100 and need wait 1 second.
r.wait_available(100)
```

#   Description

A module that provides a way for rate limit and throttle.


# Classes

## ratelimiter.RateLimiter

**Synopsis**:

**syntax**:
`RateLimiter(permits, max_burst=1)`

**arguments**:

-   `permits`:
    specifies the permits per second.
    It can be a int, float, long value.
    If permits is 1, it means we can get 1 permit one second.

-   `max_burst`
    specifies the permits that can max stored in second.
    Default is 1 second.
    If permits is 2/s, and max_burst is specified as 2 seconds,
    the max capacity we can hold is 2 * 2 = 4 permits.

### RateLimiter.consume
Reduce the permits capacity according to consumed permits.

**syntax**:
`RateLimiter.consume(consumed)`

**arguments**:

-   `consumed`:
    specifies already consumed permits.

**return**:
Nothing.

### RateLimiter.wait_available
Wait util the request permits is available.

**syntax**:
`RateLimiter.wait_available(request)`

**arguments**:

-   `request`:
    specifies the request permits.
    This will lead to a time sleep if stored permits is not enough.

**return**:
Nothing.

### RateLimiter.set_permits
set the permits in second.

**syntax**:
`RateLimiter.set_permits(permits)`

**arguments**:

-   `permits`:
    specifies the permits per second.
    This will lead to stored permits and max stored permits resize.

**return**:
Nothing.

### RateLimiter.get_stored
get the stored permits in RateLimiter.

**syntax**:
`RateLimiter.get_stored`

**return**:
the stored permits in RateLimiter.
It can be a negative value for debt.

#   Author

Tongwei Liu (刘桐伟) <tongwei.liu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Tongwei Liu (刘桐伟) <tongwei.liu@baishancloud.com>
