<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Methods](#methods)
  - [dictutil.depth_iter](#dictutildepth_iter)
  - [dictutil.breadth_iter](#dictutilbreadth_iter)
  - [dictutil.make_getter](#dictutilmake_getter)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

dictutil

It provides with several dict operation functions.

#   Status

This library is considered production ready.

#   Synopsis

Depth first search a dictionary

```python
from pykit import dictutil

mydict = {'k1':
             {'k11': 'v11',
              'k12': {'k121': 'v121'},
              'k13': {'k131': {'k1311': 'v1311'}}
             }
         }

# depth-first iterative the dict
for rst in dictutil.depth_iter(mydict):
    print rst

# output:
#     (['k1', 'k13', 'k131', 'k1311'], 'v1311')
#     (['k1', 'k12', 'k121'], 'v121')
#     (['k1', 'k11'], 'v11')
```

Breadth first search a dictionary

```python
for rst in dictutil.breadth_iter(mydict):
    print rst

# output:
#     (['k1'], {'k13': {'k131': {'k1311': 'v1311'}}, 'k12': {'k121': 'v121'}, 'k11': 'v11'})
#     (['k1', 'k13'], {'k131': {'k1311': 'v1311'}})
#     (['k1', 'k12'], {'k121': 'v121'})
#     (['k1', 'k11'], 'v11')
#     (['k1', 'k13', 'k131'], {'k1311': 'v1311'})
#     (['k1', 'k12', 'k121'], 'v121')
#     (['k1', 'k13', 'k131', 'k1311'], 'v1311')

#
```

Make a predefined dictionary item getter.

```python
import dictutil

records = [
    {"event": 'log in',
     "time": {"hour": 10, "minute": 30, }, },

    {"event": 'post a blog',
     "time": {"hour": 10, "minute": 40, }, },

    {"time": {"hour": 11, "minute": 20, }, },

    {"event": 'log out',
     "time": {"hour": 11, "minute": 20, }, },
]

get_event = dictutil.make_getter('event', default="NOTHING DONE")
get_time = dictutil.make_getter('time.$field')

for record in records:

    ev = get_event(record)

    tm = "%d:%d" % (get_time(record, {"field": "hour"}),
                    get_time(record, {"field": "minute"}))

    print "{ev:<12}   at {tm}".format(ev=ev, tm=tm)

# output:
# log in         at 10:30
# post a blog    at 10:40
# NOTHING DONE   at 11:20
# log out        at 11:20
```

#   Methods

## dictutil.depth_iter

**syntax**:
`dictutil.depth_iter(mydict, ks=None, maxdepth=10240, get_mid=False)`

**arguments**:

-   `mydict`: the dict that you want to iterative

-   `ks`: the argument could be a `list`,  it would be seted ahead of key's list in results of iteration

    ```python
    for rst in dictutil.depth_iter(mydict, ks=['mykey1','mykey2']):
        print rst

    # output:
    #     (['mykey1', 'mykey2', 'k1', 'k13', 'k131', 'k1311'], 'v1311')
    #     (['mykey1', 'mykey2', 'k1', 'k12', 'k121'], 'v121')
    #     (['mykey1', 'mykey2', 'k1', 'k11'], 'v11')

   ```

-   `maxdepth`: specifies the max depth of iteration

    ```python
    for rst in dictutil.depth_iter(mydict, maxdepth=2):
        print rst

    # output
    #     (['k1', 'k13'], {'k131': {'k1311': 'v1311'}})
    #     (['k1', 'k12'], {'k121': 'v121'})
    #     (['k1', 'k11'], 'v11')
    ```

-   `git_mid`: if set `True`, the method will show the middle results that can be iteraived, by default it is `False`

   ```python
   for rst in dictutil.depth_iter(mydict, get_mid=True):
       print rst

   # output
   #     (['k1'], {'k13': {'k131': {'k1311': 'v1311'}}, 'k12': {'k121': 'v121'}, 'k11': 'v11'})
   #     (['k1', 'k13'], {'k131': {'k1311': 'v1311'}})
   #     (['k1', 'k13', 'k131'], {'k1311': 'v1311'})
   #     (['k1', 'k13', 'k131', 'k1311'], 'v1311')
   #     (['k1', 'k12'], {'k121': 'v121'})
   #     (['k1', 'k12', 'k121'], 'v121')
   #     (['k1', 'k11'], 'v11')

   ```

**return**:

return iterative object, each element is a tuple object contains  keys and value

## dictutil.breadth_iter

**syntax**:
`dictutil.breadth_iter(mydict)`

**arguments**:

-   `mydict`: the dict you want to iterative

**return**:

return iterative object, each element is a tuple object contains  keys and value

##  dictutil.make_getter

**syntax**:
`dictutil.make_getter(key_path, default=0)`

It creates a lambda that returns the value of the item specified by
`key_path`.

**arguments**:
-   `key_path`:
    is a dot separated path string of key hierarchy to get an item from a dictionary.

    Example: `foo.bar` is same as `some_dict["foo"]["bar"]`.

-   `default`:
    is the default value if the item is not found.
    For example when `foo.bar` is used on a dictionary `{"foo":{}}`.

    It must be a primitive value such as `int`, `float`, `bool`, `string` or `None`.

**return**:
the item value found by key_path, or the default value if not found.

#   Author

break wang (王显宝) <breakwang@outlook.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 break wang (王显宝) <breakwang@outlook.com>
