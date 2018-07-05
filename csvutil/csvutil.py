#!/usr/bin/env python2
# coding: utf-8

import csv


def to_dicts(data, fields, on_invalid=None):

    result = []

    if isinstance(data, file):
        reader = csv.reader(data)

    else:
        reader = data

    for row in reader:

        row_node = {}

        for (key, value) in zip(fields, row):

            try:
                if isinstance(key, (tuple, list,)):
                    temp = key[1](value)
                    row_node[key[0]] = temp

                else:
                    row_node[key] = value

            except Exception as e:

                if on_invalid is 'ignore':
                    break

                elif on_invalid is None:
                    raise

                else:
                    on_invalid(fields.index(key), key, value, e)

        if len(row_node) == len(fields):

            result.append(row_node)

    return result
