#!/usr/bin/env python2
# coding: utf-8

import json


def dump(obj):
    return json.dumps(obj, encoding='utf-8')


def load(s):

    if s is None:
        return None

    return json.loads(s, encoding='utf-8')
