<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Synopsis](#synopsis)
- [Methods](#methods)
  - [modutil.submodules](#modutilsubmodules)
  - [modutil.submodule_tree](#modutilsubmodule_tree)
  - [modutil.submodule_leaf_tree](#modutilsubmodule_leaf_tree)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

modutil

#   Status

This library is considered production ready.

#   Description

Submodule Utilities.


#   Synopsis


```
modutil.submodules(pykit)
#{
#    'modutil': <module> pykit.modutil,
#    ... ...
#}

modutil.submodule_tree(pykit)
#{
#    'modutil': {'module': <module> pykit.modutil,
#                'children': {
#                            'modutil': {
#                                    'module': <module> pykit.modutil.modutil,
#                                    'children': None,
#                                    },
#                            'test': {
#                                    'module': <module> pykit.modutil.test,
#                                    'children': {
#                                        'test_modutil': {
#                                            'module': <module> pykit.modutil.test.test_modutil,
#                                            'children': None,
#                                        },
#                                    },
#                            }
#                },
#               }
#    ... ...
#}

modutil.submodule_leaf_tree(pykit)
#{
#    'modutil': {
#                'modutil': <module> pykit.modutil.modutil,
#                'test': {'test_modutil': <module> pykit.modutil.test.test_modutil},
#                }
#    ... ...
#}
```


#   Methods

##  modutil.submodules

**syntax**:
`modutil.submodules(root_module)`

Load all submodules of `root_module`.
And map these submodules names to submodules.

**arguments**:

-   `root_module`:
    is a module.

**return**:
a dict whose keys are name of submodules and values are submodules loaded.
Or `{}` if no submodule loaded.
Or None if `root_module` is not the directory structure.


##  modutil.submodule_tree

**syntax**:
`modutil.submodule_tree(root_module)`

Load all submodules of `root_module` recursively. And put them in a **submodule
dict**. Every key of this dict is a submodule's name, and every value in this dict
has a 'module' part which is the submodule the key named and a 'children' part which
is the submodule dict of the 'module' part. If the 'module' part has no submodule,
the 'children' part will be assigned to `{}`. If the 'module' part is not the
directory structure, the 'children' part will be assigned to None.

**arguments**:

-   `root_module`:
    is a module.

**return**:
the submodule dict of `root_module`.
Or None if `root_module` is not the directory structure.

Example:
```
{'submod1': {'module': <module> submod1,
            'children': submodule_tree(<module> submod1),
                },
    ... ...
    }
```


##  modutil.submodule_leaf_tree

**syntax**:
`modutil.submodule_leaf_tree(root_module)`

Load all submodules of `root_module` recursively. And put them in a **submodule-leaf
dict**. Every key of this dict is a submodules' name, and every value is a
submodule-leaf dict of the submodule the key named, or the submodule itself if
the submodule is not the directory structure.
If no submodule loaded, submodule-leaf dict will be `{}`.

**arguments**:

-   `root_module`:
    is a module.

**return**:
the submodule-leaf dict of `root_module`.
Or None if `root_module` is not the directory structure.

Example:
```
{'submod1': submodule_leaf_tree( <module> submod1) or <module> submod1 }
```


#   Author

Li Wenbo (李文博) <wenbo.li@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Li Wenbo (李文博) <wenbo.li@baishancloud.com>
