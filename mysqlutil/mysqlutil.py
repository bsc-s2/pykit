#!/usr/bin/env python2
# coding: utf-8

import os

import MySQLdb
import urllib

from pykit import dictutil
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
        raise InvalidLength(
            'number of index fields and values are not equal: '
            'index fields: {fld}; '
            'index values: {val}'.format(fld=index_fields, val=index_values))


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
            req_values = [str(last_row[x]) for x in req_fields]
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


def make_sql_condition(fld_vals, operator="=", formatter=list):

    cond_expressions = []

    for k, v in fld_vals[:-1]:
        cond_expressions.append(quote(k, "`") + " = " + _safe(v))

    key, value = fld_vals[-1]
    cond_expressions.append(quote(key, "`") + " " +
                            operator + " " + _safe(value))

    return formatter(cond_expressions)


def make_insert_sql(table, values, fields=None):

    sql_pattern = "INSERT INTO {tb}{fld_clause} VALUES {val_clause};"

    tb = make_table_name(table)

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

    tb = make_table_name(table)

    set_clause = make_sql_condition(values.items(), formatter=', '.join)

    where_clause = make_where_clause(index, index_values)

    if limit is not None:
        limit_clause = ' LIMIT {n}'.format(n=limit)
    else:
        limit_clause = ''

    sql = sql_pattern.format(tb=tb, set_clause=set_clause, where_clause=where_clause,
                             limit_clause=limit_clause)

    return sql


def make_delete_sql(table, index, index_values, limit=None):

    sql_pattern = 'DELETE FROM {tb}{where_clause}{limit_clause};'

    tb = make_table_name(table)

    where_clause = make_where_clause(index, index_values)

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

    tb = make_table_name(table)

    if result_fields is None:
        rst_flds = '*'
    else:
        rst_flds = ', '.join([quote(x, "`") for x in result_fields])

    if force_index is None:
        index_fld = ''
    else:
        index_fld = ' FORCE INDEX (`{idx}`)'.format(idx=force_index)

    where_clause = make_where_clause(index, index_values, operator)

    if limit is not None:
        limit_clause = ' LIMIT {n}'.format(n=limit)
    else:
        limit_clause = ''

    sql = sql_pattern.format(rst=rst_flds, tb=tb, force_index=index_fld, where_clause=where_clause,
                             limit_clause=limit_clause)

    return sql


def make_sql_range_conditions(fields, start, end=None):

    fld_len = len(fields)

    if len(start) != fld_len:
        raise InvalidLength(
                "the number of fields in 'start' and 'shard_fields' is not equal:"
                " start: {start}"
                " fields: {fields}".format(start=start, fields=fields))

    if end is None:
        end = type(start)([None] * len(start))

    elif len(end) != fld_len:
        raise InvalidLength(
                "the number of fields in 'end' and 'shard_fields' is not equal:"
                " end: {end}"
                " fields: {fields}".format(end=end, fields=fields))

    elif start >= end:
        return []

    fld_ranges = []
    for i in xrange(fld_len):
        fld_ranges.append((fields[i], (start[i], end[i]),))

    conditions = make_range_conditions(fld_ranges)

    result = []
    for cond in conditions:

        sql_conds = []
        for fld, operator, val in cond:
            sql_conds.append(quote(fld, '`') + operator + _safe(val))

        result.append(' AND '.join(sql_conds))

    return result


def make_range_conditions(fld_ranges, left_close=True):

    result = []
    start = 0
    end = 1

    # field[i] range is [start[i], end[i]), if start equals to end, it is a blank range.
    # continuose blank ranges in the beginning should not show as:
    # `fld > start[i] and fld < end[i]` but `fld = start[i]`.
    n_pref_blank_flds = 0
    for fld, _range in fld_ranges:
        if _range[start] == _range[end]:
            n_pref_blank_flds += 1
        else:
            break

    first_effective_fld = fld_ranges[n_pref_blank_flds][0]

    len_flds = len(fld_ranges)

    # init
    operator = ' > '
    range_use = start
    n_flds_use = len_flds

    while True:

        cond = []
        for fld, _range in fld_ranges[:n_flds_use - 1]:
            cond.append((fld, ' = ', _range[range_use]))

        fld, _range = fld_ranges[n_flds_use-1]

        if range_use == start and left_close:
            cond.append((fld, ' >= ', _range[start]))
            left_close = False
        else:
            cond.append((fld, operator, _range[range_use]))

        if fld == first_effective_fld:
            # no right boundary
            if _range[end] is None:
                result.append(cond)
                return result

            cond.append((fld, ' < ', _range[end]))

            operator = ' < '
            range_use = end

        if range_use == start:
            n_flds_use -= 1
        else:
            n_flds_use += 1

        result.append(cond)

        if n_flds_use > len_flds:
            break

    return result


def make_range_mysqldump_cmd(fields, conn, db, table, path_dump_to, dump_exec, start, end=None):

    cmd_pattern = ('{dump} --host={host} --port={port} --user={user} --password={passwd}'
                   ' {db} {table} -w {cond} > {rst_path}')

    if path_dump_to is None:
        rst_path = '{table}.sql'.format(table=urllib.quote_plus(table))
    elif isinstance(path_dump_to, basestring):
        rst_path = path_dump_to
    else:
        rst_path = os.path.join(*path_dump_to)

    if dump_exec is None:
        dump = 'mysqldump'
    elif isinstance(dump_exec, basestring):
        dump = dump_exec
    else:
        dump = os.path.join(*dump_exec)

    conditions = make_sql_range_conditions(fields, start, end)
    cond_expression = '(' + ') OR ('.join(conditions) + ')'

    pattern_args = dictutil.subdict(conn, ['host', 'port', 'user', 'passwd'],
                                    use_default=True, default='')

    pattern_args['dump'] = dump
    pattern_args['db'] = db
    pattern_args['table'] = table
    pattern_args['cond'] = cond_expression
    pattern_args['rst_path'] = rst_path

    for k, v in pattern_args.items():
        pattern_args[k] = quote(str(v), "'")

    return cmd_pattern.format(**pattern_args)


def quote(s, quote):

    if quote in s:
        s = s.replace(quote, "\\" + quote)

    return quote + s + quote


def _safe(s):
    return '"' + MySQLdb.escape_string(s) + '"'


def make_table_name(table_name):

    if isinstance(table_name, basestring):
        tb = quote(table_name, "`")
    else:
        db = quote(table_name[0], "`")
        tbl = quote(table_name[1], "`")
        tb = db + '.' + tbl

    return tb


def make_where_clause(index, index_values, operator='='):

    if index is not None:
        if len(index) != len(index_values):
            raise InvalidLength(
                'number of index fields and values are not equal: '
                'index fields: {fld}; '
                'index values: {val}'.format(fld=index, val=index_values))

        where_clause = ' WHERE {cond}'.format(
            cond=make_sql_condition(zip(index, index_values), operator, formatter=' AND '.join))
    else:
        where_clause = ''

    return where_clause
