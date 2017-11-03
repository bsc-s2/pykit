<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Exceptions](#exceptions)
  - [Empty](#empty)
- [Classes](#classes)
  - [PriorityQueue](#priorityqueue)
    - [PriorityQueue.add_producer](#priorityqueueadd_producer)
    - [PriorityQueue.remove_producer](#priorityqueueremove_producer)
    - [PriorityQueue.get](#priorityqueueget)
  - [Producer](#producer)
    - [Producer.get](#producerget)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

priorityqueue

#   Status

This library is considered production ready.

#   Synopsis

`priorityqueue.get()` produces items from each producer with the same ratio of
their priority.
If a producer becomes empty, the others still respect this rule.

```python
from pykit import priorityqueue

producers = (
    # id, priority, iterable
    (1, 1, [1] * 10),
    (2, 2, [2] * 10),
    (3, 3, [3] * 10),
)
pq = priorityqueue.PriorityQueue()
for pid, prio, itr in producers:
    pq.add_producer(pid, prio, itr)

count = {}
for _ in range(12):
    val = pq.get()
    count[val] = count.get(val, 0) + 1
    print val,

print
print 'respect priority ratio: counts:', repr(count)

while True:
    try:
        val = pq.get()
    except priorityqueue.Empty as e:
        break
    count[val] = count.get(val, 0) + 1
    print val,

print
print 'consumed all: counts:', repr(count)

# 3 2 1 3 2 3 3 2 1 3 2 3
# respect priority ratio: counts: {1: 2, 2: 4, 3: 6}
# 3 2 1 3 2 3 3 2 1 2 2 1 2 1 1 1 1 1
# consumed all: counts: {1: 10, 2: 10, 3: 10}
```

#   Description

PriorityQueue is a queue with priority support:

The numbers of items it pops from each producer matches exactly the ratio of their priority:
If the priorities of 3 producer A, B and C are 1, 3 and 7, and it runs long
enough, it is expected that the number of items popped from A, B and C are
1:3:7.

#   Exceptions

##  Empty

Same as `Queue.Empty`


#   Classes


##  PriorityQueue

A queue managing several `Producer` instances.
It produces items by `Producer.priority`.

Internally, there are two heap to store producers.
One of them for all consumable producers, the other is for all empty producers.

When `PriorityQueue.get()` is called and it found that a producer becomes empty,
it remove it from the consumable heap and put it into the empty producer heap
and will never try to get an item from it again.

To re-enable a producer, call `PriorityQueue.add_producer()` with the same
`producer_id`.

**syntax**:
`PriorityQueue()`


###  PriorityQueue.add_producer

Add a new producer or reset an existent producer.

**syntax**:
`PriorityQueue.add_producer(producer_id, priority, iterable)`

**arguments**:

-   `producer_id`:
    is provided as identity of a producer.

-   `priority`:
    specifies the priority of this producer.
    `priority` also acts as the weight of item to produce.

-   `iterable`:
    is an producer implementation: it could be anything that can be used in a
    `for-in` loop, such as `[1, 2, 3]`, or `range(10)`.

**return**:
Nothing


###  PriorityQueue.remove_producer

Remove a producer by its id.

**syntax**:
`PriorityQueue.remove_producer(producer_id, ignore_not_found=False)`

**arguments**:

-   `producer_id`:
    specifies the id of a producer to remove.

-   `ignore_not_found`:
    if it is `False`, raies a `KeyError` when such a `producer_id` not found.
    Defaults to `False`.

**return**:
Nothing


###  PriorityQueue.get

Get an item from a least consumed producer.

**syntax**:
`PriorityQueue.get()`

**return**:
an item.


##  Producer

An internal class which tracks consumption state.
It provides with a `get()` method to retrieve and item from it.
It has an attribute `priority` to specify its priority.

A `Producer` instance is able to compare to another with operator `<`:

-   `a<b` is defined by: a is less consumed and would cost less for each
    consumption:

    The comparison key is: `(1/priority * nr_of_get, 1/priority)`.

Thus a smaller `Producer` means it is less consumed and should be consumed first.

**syntax**:
`Producer(producer_id, priority, iterable)`

**arguments**:

-   `producer_id`:
    specifies an id for this producer.

-   `priority`:
    specifies priority of this queue.
    Every time `get()` is called, the counter attribute `consumed` increments by
    `default_priority/priority`.

-   `iterable`:
    is an iterable variable to produce item.
    It could be a `list` such as `[1, 2, 3]`, a `generator` such as `def x(): for i in range(10): yield i`,
    or anything else that can be used in a `for-in` loop.

###  Producer.get

Returns an item.

**syntax**:
`Producer.get()`

**return**:
an item.


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
