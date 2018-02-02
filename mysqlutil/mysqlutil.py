#!/usr/bin/env python2
# coding: utf-8

import MySQLdb

from pykit import mysqlconnpool
from pykit import strutil


class ConnectionTypeError(Exception):
    pass


class IndexNotPairs(Exception):
    pass


class ShardNotPairs(Exception):
    pass


def scan_index(connpool, table, result_fields, index_fields, index_values,
               left_open=False, limit=None, index_name=None, use_dict=True, retry=0):

    if type(connpool) == dict:
        # an address
        pool = mysqlconnpool.make(connpool)
    elif isinstance(connpool, mysqlconnpool.MysqlConnectionPool):
        pool = connpool
    else:
        raise ConnectionTypeError

    if len(index_values) != len(index_fields):
        raise IndexNotPairs

    req_fields = list(index_fields)
    req_values = list(index_values)

    strict = True
    if limit is None:
        strict = False
        limit = 1024

    while True:
        sql = sql_scan_index(table, [], req_fields, req_values,
                             left_open=left_open, limit=limit, index_name=index_name)

        rst = pool.query(sql, retry=retry)

        for rr in rst:
            if use_dict:
                yield dict([(k, rr[k]) for k in result_fields])
            else:
                yield [rr[k] for k in result_fields]

        if strict:
            break

        if len(rst) > 0:
            last_row = rst[-1]
            req_fields = list(index_fields)
            req_values = [last_row[x] for x in req_fields]
            left_open = True
            continue

        req_fields = req_fields[:-1]
        req_values = req_values[:-1]
        if len(req_fields) > 0:
            continue

        break


def sql_scan_index(table, result_fields, index_fields, index_values,
                   left_open=False, limit=1024, index_name=None):

    if type(table) is str:
        table_name = quote(table)
    else:
        table_name = '.'.join([quote(t) for t in table])

    fields_to_return = ', '.join([quote(x) for x in result_fields])
    if len(fields_to_return) == 0:
        fields_to_return = '*'

    force_index = ''
    if index_name is not None:
        force_index = ' FORCE INDEX (' + quote(index_name) + ')'
    elif len(index_fields) > 0:
        force_index = ' FORCE INDEX (' + quote('idx_' + '_'.join(index_fields)) + ')'

    where_conditions = ''
    index_pairs = zip(index_fields, index_values)

    if len(index_pairs) > 0:

        conditions = []
        for pair in index_pairs[:-1]:
            conditions.append(table_name + '.' + quote(pair[0]) + ' = ' + _safe(pair[1]))

        pair = index_pairs[-1]
        if left_open:
            operator = ' > '
        else:
            operator = ' >= '

        conditions.append(table_name + '.' + quote(pair[0]) + operator + _safe(pair[1]))

        where_conditions = ' WHERE ' + ' AND '.join(conditions)

    limit = int(limit)

    sql_to_return = ('SELECT ' + fields_to_return +
                     ' FROM ' + table_name +
                     force_index +
                     where_conditions +
                     ' LIMIT ' + str(limit))

    return sql_to_return


def sql_condition_between_shards(shard_fields, start, end=None):

    if end is None:
        end = []
    elif len(shard_fields) != len(end):
        raise ShardNotPairs

    if len(shard_fields) != len(start):
        raise ShardNotPairs

    same_fields = strutil.common_prefix(start, end)
    prefix_condition = ''
    prefix_len = len(same_fields)
    if len(prefix_len) > 0:
        prefix_shards = zip(shard_fields[:prefix_len], start[:prefix_len])
        prefix_condition = connect_condition(prefix_shards, '=')
        prefix_condition += " AND "

        shard_fields = shard_fields[prefix_len:]
        start = start[prefix_len:]
        end = end[prefix_len:]

    start_shards = zip(shard_fields, start)
    start_condition_first = prefix_condition + \
        connect_condition(start_shards, '>=')
    start_condition = generate_shards_condition(
        start_shards[:-1], '>', prefix=prefix_condition)
    start_condition.insert(0, start_condition_first)

    if len(end) == 0:
        return start_condition

    end_shards = zip(shard_fields, end)
    end_condition = generate_shards_condition(
        end_shards, '<', prefix=prefix_condition)

    condition = []

    condition += start_shards[:-1]
    condition += end_shards[:-1]
    condition.append(prefix_condition +
                     start_condition[-1] + " AND " + end_condition[-1])

    return condition


def generate_shards_condition(shards, operator, prefix=''):

    conditions = []
    while len(shards) > 0:

        and_condition = prefix + connect_condition(shards, operator)
        conditions.append(and_condition)

        shards = shards[:-1]

    return conditions


def connect_condition(shards, operator):

    condition = []

    for s in shards[-1]:
        condition.append(quote(s[0]) + "=" + quote(s[1], '"'))

    s = shards[-1]
    condition.append(quote(s[0] + operator + quote(s[1], '"')))

    return " AND ".join(condition)


def quote(s, quote="`"):

    if quote in s:
        s = s.replace(quote, "\\" + quote)

    return quote + s + quote

def _safe(s):
    return '"' + MySQLdb.escape_string(s) + '"'

