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
    - [RateLimiter.set_capacity](#ratelimiterset_capacity)
    - [RateLimiter.get_stored](#ratelimiterget_stored)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

ratelimiter

#   Status

This library is considered not test well.

#   Synopsis
This module provides a way for rate limit and throttle.

We use a pre consume and get left capacity mode.
Here is the example:

```python
import time

from pykit import ratelimiter

r = throttle.RateLimiter(100, 200)

# pre consume
r.consume(1000)

# get left capacity
if r.get_stored() < 0:
   print "not enough permits"
else:
   print "can assign permits is %s" % r.get_stored()
```

#   Description

A module that provides a way for rate limit and throttle.


# Classes

## ratelimiter.RateLimiter

**Synopsis**:

**syntax**:
`RateLimiter(token_per_second, capacity)`

**arguments**:

-   `token_per_second`:
    specifies the tokens can assign per second.
    It can be a int, float, long value.
    If token is 1, it means we can get 1 token per second.

-   `capacity`
    specifies the maximum number of tokens that can be saved.

### RateLimiter.consume
Reduce the permits capacity according to consumed tokens.

**syntax**:
`RateLimiter.consume(consumed,token_time=None)`

**arguments**:

-   `consumed`:
    specifies already consumed tokens.

-   `token_time`:
    specifies the time to consume token.
    Default is None.
    If `token_time` is None, consumed from the latest stored tokens.
    If `token_time` is earlier than last consume time, consumed from stored tokens of last consume time.
    If `token_time` is later than than last consume time, consumed from tokens of the `token_time`.

**return**:
Nothing.

### RateLimiter.set_token_per_second
set the tokens in second.

**syntax**:
`RateLimiter.set_token_per_second(token_per_second)`

**arguments**:

-   `token_per_second`:
    specifies the tokens per second.

**return**:
Nothing.

### RateLimiter.set_capacity
set the capacity.

**syntax**:
`RateLimiter.set_capacity(capacity)`

**arguments**:

-   `capacity`:
    specifies the capacity.

**return**:
Nothing.

### RateLimiter.get_stored
get the stored tokens in RateLimiter.

**syntax**:
`RateLimiter.get_stored(token_time=None)`

**arguments**:

-   `token_time`:
    specifies the time to get for tokens.
    Default is None.
    If `token_time` is None, return the latest stored tokens.
    If `token_time` is earlier than last consume time,return stored tokens of last consume time.
    If `token_time` is later than than last consume time,return stored tokens of the `token_time`.

**return**:
the stored tokens in RateLimiter.
It can be a negative value for debt.

#   Author

Tongwei Liu (刘桐伟) <tongwei.liu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Tongwei Liu (刘桐伟) <tongwei.liu@baishancloud.com>
