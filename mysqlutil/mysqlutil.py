#!/usr/bin/env python2
# coding: utf-8

import MySQLdb
from pykit import mysqlconnpool


def safe(s):
    return MySQLdb.escape_string(s)


def sql_scan_index(table, result_fields, index_fields, index_values,
                   left_open=False, limit=1024, index_name=None):

    table_name = '`' + table + '`'

    fields_to_return = ', '.join(['`' + x + '`' for x in result_fields])
    if len(fields_to_return) == 0:
        fields_to_return = '*'

    force_index = ''
    if index_name is not None:
        force_index = ' FORCE INDEX (`' + index_name + '`)'
    elif len(index_fields) > 0:
        force_index = ' FORCE INDEX (`idx_' + '_'.join(index_fields) + '`)'

    conditions = []
    index_pairs = zip(index_fields, index_values)

    for i, pair in enumerate(index_pairs):

        if i < len(index_pairs) - 1:
            conditions.append(table_name + '.`' + pair[0] + '` = "' + safe(pair[1]) + '"')
            continue

        if left_open:
            conditions.append(table_name + '.`' + pair[0] + '` > "' + safe(pair[1]) + '"')
        else:
            conditions.append(table_name + '.`' + pair[0] + '` >= "' + safe(pair[1]) + '"')

    where_conditions = ''
    if len(conditions) > 0:
        where_conditions = ' WHERE ' + ' AND '.join(conditions)

    limit = int(limit)

    sql_to_return = ('SELECT ' + fields_to_return +
                     ' FROM ' + table_name +
                     force_index +
                     where_conditions +
                     ' LIMIT ' + str(limit))

    return sql_to_return


def scan_index(addr, db, table, result_fields, index_fields, index_values,
               left_open=False, limit=1024, index_name=None, use_dict=True, retry=0):

    pool = mysqlconnpool.make(addr)

    use_db = 'USE ' + '`' + db + '`'
    pool.query(use_db, retry=retry)

    sql = sql_scan_index(table, result_fields, index_fields, index_values,
                         left_open=left_open, limit=limit, index_name=index_name)

    rst = pool.query(sql, use_dict=use_dict, retry=retry)

    for rr in rst:
        yield rr
