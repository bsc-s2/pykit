#!/usr/bin/env python2
# coding: utf-8

import sys

from pykit import strutil

if __name__ == "__main__":
    args = sys.argv[1:]

    pager = args.pop(0).split()
    control_char = args.pop(0) == '1'
    limit = int(args.pop(0))
    lines = args

    strutil.page(lines, max_lines=limit, pager=pager)
