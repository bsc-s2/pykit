<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Synopsis](#synopsis)
- [Classes](#classes)
  - [rangeset.IntIncRange](#rangesetintincrange)
  - [rangeset.IntIncRangeSet](#rangesetintincrangeset)
  - [rangeset.Range](#rangesetrange)
    - [Range `&`](#range-&)
    - [Range.cmp](#rangecmp)
    - [Range.has(val)](#rangehasval)
    - [Range.is_adjacent](#rangeis_adjacent)
    - [Range.intersect](#rangeintersect)
    - [Range.substract](#rangesubstract)
    - [Range.length](#rangelength)
    - [Range.val](#rangeval)
  - [rangeset.ValueRange](#rangesetvaluerange)
    - [ValueRange.set](#valuerangeset)
  - [rangeset.RangeSet](#rangesetrangeset)
    - [RangeSet.add](#rangesetadd)
    - [RangeSet.find_overlapped](#rangesetfind_overlapped)
    - [RangeSet.has](#rangesethas)
  - [rangeset.RangeDict](#rangesetrangedict)
    - [RangeDict.add](#rangedictadd)
    - [RangeDict.get](#rangedictget)
    - [RangeDict.get_min](#rangedictget_min)
    - [RangeDict.normalize](#rangedictnormalize)
- [Methods](#methods)
  - [rangeset.union](#rangesetunion)
  - [rangeset.substract](#rangesetsubstract)
  - [rangeset.intersect](#rangesetintersect)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


#   Name

rangeset

#   Status

This library is considered production ready.

#   Description

Segmented range which is represented in a list of sorted interleaving range.

A range set can be thought as: `[[1, 2], [5, 7]]`.

#   Synopsis

```python
from pykit import rangeset
a = rangeset.RangeSet([[1, 5], [10, 20]])
a.has(1) # True
a.has(8) # False
a.add([5, 7]) # [[1, 7], [10, 20]]
```

#   Classes


## rangeset.IntIncRange

`IntIncRange` is similiar to `Range` and shares the same set of API, except it
limits value types to int or long, and its right boundary is closed, thus unlike
`Range`(right boundary is open), 2 is in `[1, 2]`.


## rangeset.IntIncRangeSet

It is similiar to `RangeSet` and shares the same set of API, except the default
class for element in it is `IntIncRange`, not `Range`.


##  rangeset.Range

**syntax**:
`rangeset.Range(left, right)`

A continuous range.
Range is left-close and right-open.
E.g. a range `[1, 3]` has 2 elements `1` and `2`, but `3` is not in this range.

**arguments**:

-   `left`:
    specifies the left close boundary, which means `left` is in in this range.

-   `right`:
    specifies the right open boundary, which means `right` is **NOT** in this
    range.

**return**:
a `rangeset.Range` instance.


### Range `&`

Overriding operator `&`.
`a & b` is the same as `a.intersect(b)`.

**syntax**:
`Range(1, 3) & Range(2, 4) # Range(2, 3)`.

**syntax**:
`Range(1, 3) & [2, 4] # Range(2, 3)`.

**syntax**:
`[1, 3] & Range(2, 4) # Range(2, 3)`.



### Range.cmp

**syntax**:
`Range.cmp(other)`

Compare this range with `other`.

**arguments**:

-   `other`:
    is another `Range` instance.

**return**:
-   `1` if this range is on the right of `other`.
-   `-1` if this range is on the left of `other`.
-   `0` if this range overlaps with `other` or they are adjacent ranges.
    E.g. `Range(1, 3)` results in 0 when comparing with these following range
    -   `Range(1, 2)`: overlapping.
    -   `Range(2, 4)`: overlapping.
    -   `Range(0, 1)`: adjacent.
    -   `Range(3, 4)`: adjacent.


###  Range.has(val)

**syntax**:
`Range.has(val)`

Return True if `val` is in this range. Otherwise `False`.

**arguments**:

-   `val`:
    is the value to check.

**return**:
`bool`


###  Range.is_adjacent

**syntax**:
`Range.is_adjacent(other)`

Check if this range is at left of `other` and they are adjacent and can be
merged into one range.

**arguments**:

-   `other`:
    is another `Range` instance.

**return**:
`True` for `[1, 2] and [2, 3]`
`False` for `[1, 2] and [3, 4]` or `[1, 2] and [1, 3]`


###  Range.intersect

**syntax**:
`Range.intersect(rng)`

Intersect this range with another range.

E.g.

```python
Range(1, 5).intersect(2, None) # Range(2, 5)
```

**arguments**:

-   `rng`: is a`list`, `Range` or `ValueRange`

**return**:
`None` if it has no itersection with `rng`, or a new instance of intersection.


###  Range.substract

**syntax**:
`Range.substract(rng)`

Remove `rng` from a range.
The result is a list of 2 `Range`.
Because `rng` might split it into two separate sub range.

**Synopsis**:

```
Range(0, 5).substract([1, 2])    # [[0, 1], [2, 5]]
Range(0, 5).substract([-1, 2])   # [None, [2, 5]]
Range(0, 5).substract([None, 6]) # [None, None]
```

**arguments**:

-   `rng`:
    is another `Range` or `list` of 2 elements that represents a range.

**return**:
a list of 2 `Range` instance.


###  Range.length

**syntax**:
`Range.length()`

Return range length if it is a numeric range such as `int`, `float` or string
range.

If it is a string range, such as `["a", "abc"]`, the length is a float number
between 0 and 1.

It treats `a` and `b` as two base-257 float `va = 0.a[0]a[1]...` and
`vb = 0.b[0]b[1]...`.
And we define the length to be `vb - va`.

For `i >= len(a)` `a[i]` is defined to be 0,
Otherwize, `a[i]` is defined to be `ord(a[i]) + 1`.
Thus:

-   empty string `""` is 0,
-   `"\0"` is 1,
-   `"a"` is `0x62`(ascii of `"a"` is `0x61`).

There are 257 possible value: empty string `""` and 256 chars `"\x00" ~ "\xff"`.

In python the length of `[str(a), str(b)]` is defined as:
```
sum([ (b[i] - a[i]) / 257.0**(i+1)
      for i in range(0, max([len(a), len(b)]))
])
```


**return**:
length in the same type of one of its boundary.

If one of left and right boundary is `None`, in which case it is an infite
range, `float('inf')` is returned.

###  Range.val

**syntax**:
`Range.val()`

**return**:
The value of range associated.


##  rangeset.ValueRange

**syntax**:
`rangeset.ValueRange(left, right, val=None)`

It maps a range to a value.
E.g.: `ValueRange(0, 1, 'foo')` defines that value for `[0, 1)` is `"foo"`.

A `ValueRange` is left-close and right-open.

`ValueRange` has the same methods as `Range`.


###  ValueRange.set

**syntax**:
`ValueRange.set(v)`

**arguments**:

-   `v`:
    the value to update to this range.

**return**:
Nothing


##  rangeset.RangeSet

**syntax**:
`rangeset.RangeSet(ranges)`

A series of int `Range`.
All ranges in it are ascending ordered, non-overlapping and non-adjacent.

**arguments**:

-   `ranges`:
    is a list of range.

###  RangeSet.add

**syntax**:
`RangeSet.add(rng)`

It adds a new range into this range set and if possible, collapse it with
overlapping or adjacent range.

Synopsis:

```
RangeSet([[10, 20], [30, 40]].add([19, 30]) # [[10, 40]]
RangeSet([[10, 20], [30, 40]].add([0, 35])  # [[0, 40]]
```

**arguments**:

-   `rng`:
    is a `Range` or a 2 element tuple or list.

**return**:
nothing, but modify the range-set in place.


###  RangeSet.find_overlapped

**syntax**:
`RangeSet.find_overlapped(rng)`

Find all ranges those overlaps with `rng`.
E.g.

```python

RangeSet([[None, 10], [20, 30], [40, None]]).find_overlapped([29, 41])
# RangeSet([[20, 30, 'b'], [40, None, 'c']])
```

**arguments**:

-   `rng`:
    a range iterable with at least 2 elements, such `list`, `tuple`, `Range` or
    `ValueRange`.

**return**:
a instance of `self.__class__` with `Range` or `ValueRange` elements those
overlaps with `rng`.


###  RangeSet.has

**syntax**:
`RangeSet.has(val)`

Checks if a `val` is in any of the range segments.

Synopsis:

```python
RangeSet([[10, 20], [30, 40]]).has(1)  # False
RangeSet([[10, 20], [30, 40]]).has(10) # True
RangeSet([[10, 20], [30, 40]]).has(20) # False
RangeSet([[10, 20], [30, 40]]).has(25) # False
RangeSet([[10, 20], [30, 40]]).has(30) # True
RangeSet([[10, 20], [30, 40]]).has(50) # False
```

**arguments**:

-   `val`:
    is the value to check.

**return**:
`True` if `val` is in it. Or `False`.



##  rangeset.RangeDict

**syntax**:
`rangeset.RangeDict(iterable=None, range_clz=None, dimension=None)`

`RangeDict` defines a mapping from ranges to values.
E.g.:

```
rd = RangeDict([(0, 1, 'foo'), (1, 2, 'bar')])
rd.get(0)   # 'foo'
rd.get(1)   # 'bar'
rd.get(1.5) # 'bar'
rd.get(2)   # KeyError
```

**Difference from `RangeSet`**:
Adjacent ranges such as `(0, 1), (1, 2)` can exist in `RangeDict`
but can not exist in `RangeSet`.
Because in `RangeDict` each range there is a value bound.

**arguments**:
are same as `RangeSet` except the default value for `range_clz` is `ValueRange`
instead of `Range`.

-   `dimension`:
    specifies if to convert the value in it into a nested `RangeDict`.
    It is used to create multi dimension RangeDict.
    By default it is `1`.

    **Synopsis**:

    ```python
    """
    A sample of 2d mapped value: time(t) and a string range:
    This setting split the entire plain into 4 areas.

        range
        ^
        |
      d +----+----+
        |    | cd |
      c + bd +----+
        |    |    |
      b +----+    |
        | ab | ac |
      a +----+----+
        |
     '' +----+----+--------> t
        0    1    2
    """

    inp = [
            [0, 1, [['a', 'b', 'ab'],
                    ['b', 'd', 'bd'],
            ]],
            [1, 2, [['a', 'c', 'ac'],
                    ['c', 'd', 'cd'],
            ]],
    ]

    r = rangeset.RangeDict(inp, dimension=2)

    print r.get(0.5, 'a') # 'ab'
    print r.get(1.5, 'a') # 'ac'
    ```

> One of a useful scenario for 2d `RangeDict` is to store sharding info.
> Because sharding config might change, there might be a migration period a server
> needs two config.
>
> With the following example:
>
> ```
>     range
>     ^
>     |
>   d +----+----+
>     |    | cd |
>   c + bd +----+
>     |    |    |
>   b +----+    |
>     | ab | ac |
>   a +----+----+
>     |
>  '' +----+----+--------> t
>     0    1    2
> ```
>
> At first(before time `1`) we store keys start with `a ~ b` in database `ab`,
> and keys start with `b ~ d` in database `bd`.
>
> At time `1` the administrator decide to re-balance all keys with a new
> sharding config:
> storing keys starts with `a ~ c` in database `ac`,
> and keys start with `c ~ d` in database `cd`.
>
> All API servers must be aware of the config change in order to run a dual-read
> mechanism.
> E.g. to read a key `bb`:
>
> -   First read it from the latest configured database `ac`, if not found:
> -   Then read it from database `bd`: the previous shard for `bb`.
>
> This way it let the system to smoothly transfer from one config to another.

Methods of `RangeDict` are the same as `RangeSet` except the following three:


###  RangeDict.add

**syntax**:
`RangeDict.add(rng, val)`

Add a mapping from range to value into `RangeDict`.

**arguments**:

-   `rng`:
    a two element iterable that defines a range.

-   `val`:
    value of any data type.

**return**:
Nothing


###  RangeDict.get

**syntax**:
`RangeDict.get(pos, *positions)`

**arguments**:

-   `pos`:
    position in `RangeDict`

-   `positions`:
    the nested position to get if this `RangeDict.dimension > 1`.

**return**:
the value of range that `pos` is in.

If `pos` is not in any ranges, `KeyError` is raised.


### RangeDict.get_min

**syntax**:
`RangeDict.get_min(is_lt=None)`

Get range of the minimum value in the range dict. If minmum value has more than one range, then get
the first one.

**argument**:

-   `is_lt`:
    is a function that receives 2 arguments `a` and `b`, returns `True` if `a` is "smaller" than `b`,
    otherwise return `False`.
    Example:
    ```
    def is_lt(a, b):
        return a < b
    ```
    If `is_lt` is `None`, use `a < b` to decide 'a' is smaller than 'b'.

**return**:
- `i`:
    the index of the minimum value in the range dict.

- `rng`:
    a `ValueRange`, which is the range of the minimum value in the range dict.

- `val`:
    the minimum value in the range dict.

If range dict is empty, `ValueError` is raised.


###  RangeDict.normalize

**syntax**:
`RangeDict.normalize()`

Reduce number of elements by
merging adjacent ranges those have the same value into one continuous range.

**Values are compared with `==`, not `is`**

E.g.:

```python
rd = rangeset.RangeDict([(1, 2, '12'), [2, 3, '12']])
rd.normalize() # [[1, 3, '12']]
```

**return**:
Nothing.


#   Methods

##  rangeset.union

**syntax**:
`rangeset.union(a, *others)`

Return a new union set `RangeSet` of all `a` and `others`.

```
rangeset.union(
    rangeset.RangeSet([[None, 10], [20, 30], [40, None]]),
    rangeset.RangeSet([[11, 22]])
)
# [[None, 10], [11, 30], [40, None]]
```

**arguments**:

-   `a`:
    a `RangeSet` instance.

-   `others`:
    `RangeSet` instances

**return**:
a new `RangeSet` instance.


##  rangeset.substract

**syntax**:
`rangeset.substract(a, *others)`

Return a new `RangeSet` with all ranges in `others` removed from `a`.

```
rangeset.substract(
    rangeset.RangeSet([[None, 10], [20, 30], [40, None]]),
    rangeset.RangeSet([[25, 45]])
)
# [[None, 10], [20, 25], [45, None]]
```

**arguments**:

-   `a`:
    a `RangeSet` instance.

-   `others`:
    `RangeSet` instances

**return**:
a new `RangeSet` instance.


##  rangeset.intersect

**syntax**:
`rangeset.intersect(a, *others)`

Return a new intersection set `RangeSet` of all `a` and `others`.

> intersect(a, b): a^b is defined with substraction: a^b = a - (a - b)


**arguments**:

-   `a`:
    a `RangeSet` instance.

-   `others`:
    `RangeSet` instances.

**return**:
a new `RangeSet` instance.


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
