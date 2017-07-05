#!/usr/bin/env python2
# coding: utf-8

import copy
import sys

def command_normal(**argkv):

    argkv = copy.deepcopy(argkv)

    if '_add_help' in argkv:
        del argkv['_add_help']

    args = sys.argv[1:]
    root = argkv

    try:
        while len(args) > 0 and root.has_key(args[0]):

            node = root[args[0]]
            args.pop(0)

            if callable(node):
                try:
                    rc = node(*args)
                    sys.exit(0
                              if rc is True or rc is 0 or rc is None
                              else 1)
                except Exception as e:
                    sys.stderr.write(repr(e))
                    sys.exit(1)
            else:
                root = node

        sys.stderr.write('No such command: ' + ' '.join(sys.argv[1:]))
        sys.exit(2)
    except Exception as e:
        sys.stderr.write(repr(e))
        sys.exit(1)

