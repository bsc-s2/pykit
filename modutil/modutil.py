#!/usr/bin/env python2
# coding: utf-8

import os
import pkgutil


def submodules(root_module):

    mod_path = root_module.__file__

    fn = os.path.basename(mod_path)
    pathname = os.path.dirname(mod_path)

    if fn not in ("__init__.py", "__init__.pyc"):
        return None

    rst = {}

    for imp, name, _ in pkgutil.iter_modules([pathname]):
        loader = imp.find_module(name)
        mod = loader.load_module(root_module.__name__ + "." + name)
        rst[name] = mod

    return rst


def submodule_tree(root_module):

    rst = submodules(root_module)
    if rst is None:
        return None

    for name, mod in rst.items():
        children = submodule_tree(mod)
        rst[name] = {"module": mod, "children": children}

    return rst


def submodule_leaf_tree(root_module):

    rst = submodules(root_module)
    if rst is None:
        return None

    for name, mod in rst.items():
        children = submodule_leaf_tree(mod)
        if children is None:
            rst[name] = mod
        else:
            rst[name] = children

    return rst
