#!/usr/bin/env python2
# coding: utf-8

import sys

fn = '/tmp/foo'


def write_file(fn, cont):
    try:
        with open(fn, 'w') as f:
            f.write(cont)
    except Exception:
        raise


if __name__ == '__main__':
    args = sys.argv[1:]
    write_file(fn, ''.join(args))
