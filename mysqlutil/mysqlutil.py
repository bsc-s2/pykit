#!/usr/bin/env python2
# coding: utf-8

import MySQLdb
from pykit import mysqlconnpool


class ConnectionTypeError(Exception):
    pass


class IndexNotPairs(Exception):
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
        table_name = _quote(table)
    else:
        table_name = '.'.join([_quote(t) for t in table])

    fields_to_return = ', '.join([_quote(x) for x in result_fields])
    if len(fields_to_return) == 0:
        fields_to_return = '*'

    force_index = ''
    if index_name is not None:
        force_index = ' FORCE INDEX (' + _quote(index_name) + ')'
    elif len(index_fields) > 0:
        force_index = ' FORCE INDEX (' + _quote('idx_' + '_'.join(index_fields)) + ')'

    where_conditions = ''
    index_pairs = zip(index_fields, index_values)

    if len(index_pairs) > 0:

        conditions = []
        for pair in index_pairs[:-1]:
            conditions.append(table_name + '.' + _quote(pair[0]) + ' = ' + _safe(pair[1]))

        pair = index_pairs[-1]
        if left_open:
            operator = ' > '
        else:
            operator = ' >= '

        conditions.append(table_name + '.' + _quote(pair[0]) + operator + _safe(pair[1]))

        where_conditions = ' WHERE ' + ' AND '.join(conditions)

    limit = int(limit)

    sql_to_return = ('SELECT ' + fields_to_return +
                     ' FROM ' + table_name +
                     force_index +
                     where_conditions +
                     ' LIMIT ' + str(limit))

    return sql_to_return


def _safe(s):
    return '"' + MySQLdb.escape_string(s) + '"'


def _quote(s):
    return '`' + s + '`'
