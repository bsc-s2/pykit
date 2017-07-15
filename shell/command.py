#!/usr/bin/env python2
# coding: utf-8

import copy
import sys
import logging
import os

logger = logging.getLogger(__name__)

def command(**kwargs):

    kwargs = copy.deepcopy(kwargs)

    args = sys.argv[1:]
    root = kwargs
    cmd = []

    try:
        while len(args) > 0 and root.has_key(args[0]):

            node = root[args[0]]
            cmd.append(args[0])
            args.pop(0)

            if callable(node):
                try:
                    logger.debug("command: " + repr(cmd) + ' args ' + repr(args) + 'cwd: ' + repr(os.getcwd()))
                    rc = node(*args)
                    sys.exit(0
                              if rc is True or rc is 0 or rc is None
                              else 1)
                except Exception as e:
                    logger.exception(repr(e))
                    sys.stderr.write(repr(e))
                    sys.exit(1)
            else:
                root = node

        sys.stderr.write('No such command: ' + ' '.join(sys.argv[1:]))
        sys.exit(2)
    except Exception as e:
        logger.exception(repr(e))
        sys.stderr.write(repr(e))
        sys.exit(1)

