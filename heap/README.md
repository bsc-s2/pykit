<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Exceptions](#exceptions)
  - [Duplicate](#duplicate)
  - [Empty](#empty)
  - [NotFound](#notfound)
- [Classes](#classes)
  - [Node](#node)
    - [Node.__lt__](#node__lt__)
    - [Node.min_child](#nodemin_child)
  - [Primitive](#primitive)
  - [RefHeap](#refheap)
    - [RefHeap.get](#refheapget)
    - [RefHeap.pop](#refheappop)
    - [RefHeap.pop_all](#refheappop_all)
    - [RefHeap.push](#refheappush)
    - [RefHeap.remove](#refheapremove)
    - [RefHeap.sift](#refheapsift)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


#   Name

heap

#   Status

This library is considered production ready.

#   Synopsis

```python
from pykit import heap

h = heap.RefHeap([5, 1, 4, 2, 3])

while h.size > 0:
    print h.pop(),
print
# 1 2 3 4 5
```

#   Description

In this module `RefHeap` is a binary min heap implemented with `reference`:
a parent has two references to two children and a child has a `parent` reference to
its parent.

`RefHeap` is not thread safe.

**Why do we need it since python provides with module `heapq`**.

-   `heapq` does not support changing heap node key, after heap created.
    But sometimes we need to adjust heap node key to bubble up a node or push
    down a node.

-   `heapq` does not support locating the index by an object reference in its
    underlying list.
    Thus if a node changed, it is not possible to find it in `O(1)` or `O(log(n))`
    time(because the underlying list is not sorted).

**`RefHeap` allows to have multiple same primitive type object in it but does NOT
allow to have two same non-primitive type objects in it**.
Thus:

```python
h = heap.RefHeap()

x = []
h.push(x)
h.push(x)  # ValueError
h.push([]) # OK
```

#   Exceptions


##  Duplicate

Indicates that an non-primitive object is already in a heap when `push()`.

**syntax**:
`Duplicate()`


##  Empty

Indicates that a heap is empty when `get()`.

**syntax**:
`Empty()`


##  NotFound

Indicates that an object is not found in a heap when `sift()` or `remove()`.

**syntax**:
`NotFound()`


#   Classes

##  Node

`Node` is a node in heap.
It is a sub class of `list` and `Node[0], Node[1]` are left and right child in a
heap.

**syntax**:
`Node(userdata)`

**arguments**:

-   `userdata`:
    user data.

###  Node.__lt__

`__lt__` let two `Node` can be compared with operator `<`.
It returns `True` or `False`.

A heap needs only a `less than` operation to work.

**syntax**:
`Node.__lt__(b)`

**arguments**:

-   `b`:
    is another `Node` instance.

**return**:
`True` or `False`


###  Node.min_child

It returns the smaller child.
**A `None` child is never a smaller one**.
`min_child` is used when heap moves a node downwards.

**syntax**:
`Node.min_child()`

**return**:
a smaller left or right child, which is a `Node` instance, or `None` if both
children are `None`.


##  Primitive

It is a wrapper class to convert a primitive type object to a reference object.
A user does not need to use this class directly.

**syntax**:
`Primitive(obj)`

**arguments**:

-   `obj`:
    a primitive type object such as `int`, `long` or `str` etc.

**return**:
`Primitive` instance.


##  RefHeap

Min-heap implemented with reference instead of a list as underlying storage.

**syntax**:
`RefHeap(iterable)`

**arguments**:

-   `iterable`:
    specifies the items to push to heap after initialized.


###  RefHeap.get

Return the minimal object, but does not remove it.
If a heap is empty an `heap.Empty` error is raised.

**syntax**:
`RefHeap.get()`

**return**:
the minimal object.


###  RefHeap.pop

Remove and return the minimal object in the heap(the root).
If a heap is empty an `heap.Empty` error is raised.

**syntax**:
`RefHeap.pop()`

**return**:
the minimal object.


###  RefHeap.pop_all

Pops all item and returns them in a list.

**syntax**:
`RefHeap.pop_all(map=lambda x:x)`

**arguments**:

-   `map`:
    specifies what to do on each popped item before returning them.
    By default it is `lambda x:x`, which does nothing.

**return**:
a list of all item in heap.


###  RefHeap.push

Push an object into a heap.

**syntax**:
`RefHeap.push(obj)`

**arguments**:

-   `obj`:
    is any type object.
    **A primitive type object is wrapped with Primitive() internally. But it
    does not affect an end user at all**.

**return**:
Nothing


###  RefHeap.remove

Remove a reference type object from heap.

**syntax**:
`RefHeap.remove(obj)`

**arguments**:

-   `obj`:
    is a previously added object.
    If `obj` does not present in this heap, `KeyError` raises.

**return**:
the object being removed.


###  RefHeap.sift

Adjust position of an object in heap when the object changed.

**Synopsis**:

```python
a, b = [1], [2]
h = heap.RefHeap([a, b])

h.get()   # a=[1]

a[0] = 3
h.sift(a) # a becomes greater and is moved downwards
h.get()   # b=[2]

b[0] = 5
h.sift(b) # b becomes greater and is moved downwards
h.get()   # a=[3]
```

**syntax**:
`RefHeap.sift(obj)`

**arguments**:

-   `obj`:
    must be an object that is already in this heap.
    Primitive object does not support `sift()`, because it is impossible to
    change its state without changing itself.

**return**:
Nothing


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
