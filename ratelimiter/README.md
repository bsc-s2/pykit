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
    - [RateLimiter.set_token_per_second](#ratelimiterset_token_per_second)
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

One is pre consume and get left capacity, another is request and wait timeout mode.
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

# request and wait timeout
r = throttle.RateLimiter(100, 2)
# this will request 100 and wait 1 second.
print r.try_acquire(100,timeout=2)
# True
```

#   Description

A module that provides a way for rate limit and throttle.


# Classes

## ratelimiter.RateLimiter

**Synopsis**:

**syntax**:
`RateLimiter(token_per_second, max_burst=1)`

**arguments**:

-   `token_per_second`:
    specifies the tokens can assign per second.
    It can be a int, float, long value.
    If token is 1, it means we can get 1 token per second.

-   `burst_second`
    specifies the maximum number of tokens that can be saved in terms of time.
    Default is 1.
    If `token_per_second` is 2/s, and burst_second is specified as 2 seconds,
    the max capacity we can hold is 2 * 2 = 4 tokens.

### RateLimiter.consume
Reduce the permits capacity according to consumed tokens.

**syntax**:
`RateLimiter.consume(consumed)`

**arguments**:

-   `consumed`:
    specifies already consumed tokens.

**return**:
Nothing.

### RateLimiter.set_token_per_second
set the tokens in second.

**syntax**:
`RateLimiter.set_token_per_second(token_per_second)`

**arguments**:

-   `token_per_second`:
    specifies the tokens per second.
    This will lead to stored tokens and max stored tokens resize.

**return**:
Nothing.

### RateLimiter.get_stored
get the stored tokens in RateLimiter.

**syntax**:
`RateLimiter.get_stored`

**return**:
the stored tokens in RateLimiter.
It can be a negative value for debt.

#   Author

Tongwei Liu (刘桐伟) <tongwei.liu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Tongwei Liu (刘桐伟) <tongwei.liu@baishancloud.com>
