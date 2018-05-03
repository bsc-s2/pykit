#!/usr/bin/env python2
# coding: utf-8

import MySQLdb
from pykit import mysqlconnpool


class ConnectionTypeError(Exception):
    pass


class InvalidLength(Exception):
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
        raise InvalidLength('number of index fields and values are not equal')

    req_fields = list(index_fields)
    req_values = list(index_values)

    strict = True
    if limit is None:
        strict = False
        limit = 1024

    while True:
        sql = make_index_scan_sql(table, None, req_fields, req_values,
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


def make_index_scan_sql(table, result_fields, index, index_values, left_open=False, limit=1024, index_name=None):

    if left_open:
        operator = '>'
    else:
        operator = '>='

    if index_name is not None:
        force_index = index_name
    elif index is not None:
        force_index = 'idx_' + '_'.join(index)
    else:
        force_index = None

    return make_select_sql(table, result_fields, index, index_values, limit, force_index, operator)


def make_sql_condition(fld_vals, operator="=", callback=list):

    cond_expressions = []

    for k, v in fld_vals[:-1]:
        cond_expressions.append(quote(k, "`") + " = " + _safe(v))

    key, value = fld_vals[-1]
    cond_expressions.append(quote(key, "`") + " " +
                            operator + " " + _safe(value))

    return callback(cond_expressions)


def make_insert_sql(table, values, fields=None):

    sql_pattern = "INSERT INTO {tb}{fld_clause} VALUES {val_clause};"

    if isinstance(table, basestring):
        tb = quote(table, '`')
    else:
        db = quote(table[0], '`')
        table_name = quote(table[1], '`')
        tb = db + '.' + table_name

    if fields is not None:
        fld_clause = ' ({flds})'.format(
            flds=', '.join([quote(fld, "`") for fld in fields]))
    else:
        fld_clause = ''

    val_clause = '({vals})'.format(
        vals=', '.join([_safe(val) for val in values]))

    sql = sql_pattern.format(
        tb=tb, fld_clause=fld_clause, val_clause=val_clause)

    return sql


def make_update_sql(table, values, index, index_values, limit=None):

    sql_pattern = "UPDATE {tb} SET {set_clause}{where_clause}{limit_clause};"

    if isinstance(table, basestring):
        tb = quote(table, '`')
    else:
        db = quote(table[0], '`')
        table_name = quote(table[1], '`')
        tb = db + '.' + table_name

    set_clause = make_sql_condition(values.items(), callback=', '.join)

    if index is not None:
        if len(index) != len(index_values):
            raise InvalidLength(
                'number of index fields and values are not equal')

        where_clause = ' WHERE {cond}'.format(
            cond=make_sql_condition(zip(index, index_values), callback=' AND '.join))
    else:
        where_clause = ''

    if limit is not None:
        limit_clause = ' LIMIT {n}'.format(n=limit)
    else:
        limit_clause = ''

    sql = sql_pattern.format(tb=tb, set_clause=set_clause, where_clause=where_clause,
                             limit_clause=limit_clause)

    return sql


def make_delete_sql(table, index, index_values, limit=None):

    sql_pattern = 'DELETE FROM {tb}{where_clause}{limit_clause};'

    if isinstance(table, basestring):
        tb = quote(table, '`')
    else:
        db = quote(table[0], '`')
        table_name = quote(table[1], '`')
        tb = db + '.' + table_name

    if index is not None:
        if len(index) != len(index_values):
            raise InvalidLength(
                'number of index fields and values are not equal')

        where_clause = ' WHERE {cond}'.format(
            cond=make_sql_condition(zip(index, index_values), callback=' AND '.join))
    else:
        where_clause = ''

    if limit is not None:
        limit_clause = ' LIMIT {n}'.format(n=limit)
    else:
        limit_clause = ''

    sql = sql_pattern.format(
        tb=tb, where_clause=where_clause, limit_clause=limit_clause)

    return sql


def make_select_sql(table, result_fields, index, index_values,
                    limit=None, force_index=None, operator='='):

    sql_pattern = 'SELECT {rst} FROM {tb}{force_index}{where_clause}{limit_clause};'

    if isinstance(table, basestring):
        tb = quote(table, "`")
    else:
        db = quote(table[0], "`")
        tbl = quote(table[1], "`")
        tb = db + '.' + tbl

    if result_fields is None:
        rst_flds = '*'
    else:
        rst_flds = ', '.join([quote(x, "`") for x in result_fields])

    if force_index is None:
        index_fld = ''
    else:
        index_fld = ' FORCE INDEX (`{idx}`)'.format(idx=force_index)

    if index is not None:
        if len(index) != len(index_values):
            raise InvalidLength(
                'number of index fields and values are not equal')

        where_clause = ' WHERE {cond}'.format(
            cond=make_sql_condition(zip(index, index_values), operator, callback=' AND '.join))
    else:
        where_clause = ''

    if limit is not None:
        limit_clause = ' LIMIT {n}'.format(n=limit)
    else:
        limit_clause = ''

    sql = sql_pattern.format(rst=rst_flds, tb=tb, force_index=index_fld, where_clause=where_clause,
                             limit_clause=limit_clause)

    return sql


def quote(s, quote):

    if quote in s:
        s = s.replace(quote, "\\" + quote)

    return quote + s + quote


def _safe(s):
    return '"' + MySQLdb.escape_string(s) + '"'


def _quote(s):
    return '`' + s + '`'
