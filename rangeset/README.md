<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Synopsis](#synopsis)
- [Classes](#classes)
  - [rangeset.Range](#rangesetrange)
    - [Range.cmp](#rangecmp)
    - [Range.is_adjacent](#rangeis_adjacent)
  - [rangeset.RangeSet](#rangesetrangeset)
    - [RangeSet.add](#rangesetadd)
    - [RangeSet.has](#rangesethas)
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

##  rangeset.Range

**syntax**:
`rangeset.Range(left, right, element_type=None)`

A continuous range.
Range is left-close and right-open.
E.g. a range `[1, 3]` has 2 elements `1` and `2`, but `3` is not in this range.

**arguments**:

-   `left`:
    specifies the left close boundary, which means `left` is in in this range.

-   `right`:
    specifies the right open boundary, which means `right` is **NOT** in this
    range.

-   `element_type`:
    specifies the data type of value in this range.
    If it is `None`, `element_type` is detected by one of the non-None `left` or
    `right`.
    If `element_type`, `left` and `right` are all `None`, use `int` by default.

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

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
