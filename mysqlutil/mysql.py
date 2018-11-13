#!/usr/bin/env python2
# coding: utf-8

import jinja2
from MySQLdb.connections import Connection

from pykit.mysqlconnpool import MysqlConnectionPool
from pykit.mysqlconnpool import conn_query


def query_by_jinja2(conn_argkw, jinja2_argkw):
    call_argkw = {}
    if isinstance(conn_argkw, dict):
        pool = MysqlConnectionPool(conn_argkw)
        func = pool.query

    elif isinstance(conn_argkw, MysqlConnectionPool):
        func = conn_argkw.query

    elif isinstance(conn_argkw, Connection):
        func = conn_query
        call_argkw['conn'] = conn_argkw

    else:
        raise TypeError('expected MysqlConnectionPool, MySQLdb.Connection '
                        'or an address(dict) but got {t}'.format(t=conn_argkw))

    if 'template' in jinja2_argkw:
        content = jinja2_argkw['template']
        env = jinja2.Environment()
        temp = env.from_string(content)

    elif 'template_path' in jinja2_argkw:
        fpath = jinja2_argkw['template_path']
        temp_loader = jinja2.FileSystemLoader(searchpath='/')
        temp_env = jinja2.Environment(loader=temp_loader, undefined=jinja2.StrictUndefined)
        temp = temp_env.get_template(fpath)

    else:
        raise ValueError('template and template_path not found in {j}'.format(j=jinja2_argkw))

    vars_ = jinja2_argkw.get('vars') or {}
    content = temp.render(vars_)
    call_argkw['sql'] = content

    return func(**call_argkw)
