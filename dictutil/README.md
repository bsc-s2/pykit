<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Methods](#methods)
  - [dictutil.depth_iter](#dictutildepth_iter)
  - [dictutil.breadth_iter](#dictutilbreadth_iter)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

dictutil

It provides with several dict operation functions.

#   Status

This library is considered production ready.

#   Synopsis

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


# breadth-first iterative the dict
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

```

#   Methods

## dictutil.depth_iter

**syntax**:
`dictutil.depth_iter(mydict, ks=None, maxdepth=10240, get_mid=False)`

**arguments**:

-   `mydict`: the dict that you want to iterative

-   `ks`: the argument could be a `list`,  it would be seted ahead of key's list in results of iteration

    ```python
<<<<<<< HEAD

=======
>>>>>>> update README.md
    for rst in dictutil.depth_iter(mydict, ks=['mykey1','mykey2']):
        print rst

    # output:
    #     (['mykey1', 'mykey2', 'k1', 'k13', 'k131', 'k1311'], 'v1311')
    #     (['mykey1', 'mykey2', 'k1', 'k12', 'k121'], 'v121')
    #     (['mykey1', 'mykey2', 'k1', 'k11'], 'v11')

   ```

-   `maxdepth`: specifies the max depth of iteration

    ```python
<<<<<<< HEAD

=======
>>>>>>> update README.md
    for rst in dictutil.depth_iter(mydict, maxdepth=2):
        print rst

    # output
    #     (['k1', 'k13'], {'k131': {'k1311': 'v1311'}})
    #     (['k1', 'k12'], {'k121': 'v121'})
    #     (['k1', 'k11'], 'v11')
    ```

-   `git_mid`: if set `True`, the method will show the middle results that can be iteraived, by default it is `False`

   ```python
<<<<<<< HEAD

=======
>>>>>>> update README.md
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

#   Author

break wang (王显宝) <breakwang@outlook.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 break wang (王显宝) <breakwang@outlook.com>
