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
    - [Range.cmp](#rangecmp)
    - [Range.has(val)](#rangehasval)
    - [Range.is_adjacent](#rangeis_adjacent)
    - [Range.length](#rangelength)
  - [rangeset.RangeSet](#rangesetrangeset)
    - [RangeSet.add](#rangesetadd)
    - [RangeSet.has](#rangesethas)
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
`Fales` for `[1, 2] and [3, 4]` or `[1, 2] and [1, 3]`


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
