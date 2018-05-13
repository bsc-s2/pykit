#!/usr/bin/env python
# coding: utf-8


class ZKUtilError(Exception):
    pass


class ZKWaitTimeout(ZKUtilError):
    pass
