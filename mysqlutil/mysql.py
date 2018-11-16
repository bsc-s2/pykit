#!/usr/bin/env python2
# coding: utf-8

import re
import jinja2
from MySQLdb.connections import Connection

from pykit.mysqlconnpool import MysqlConnectionPool
from pykit.mysqlconnpool import conn_query

from . import privilege


def _get_query_func(conn_argkw):
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

    return func, call_argkw


def validate_privileges(privs):
    if isinstance(privs, basestring):
        privs = privs.split(',')

    all_privs = privilege.privileges
    rst = []

    for p in privs:
        p = p.strip()
        if p not in all_privs:
            raise ValueError('invalid privileges: {p} not in {ps}'.format(p=p, ps=all_privs))

        rst.append(','.join(all_privs[p]))

    return rst


def _normalize_priv(priv):
    if isinstance(priv, basestring):
        g = re.match('(.*)\.(.*):(.*)', priv)
        if g is None or len(g.groups()) != 3:
            raise ValueError('invalid privileges: expected format <db>.<table>:priv, '
                             'but got: {p}'.format(p=priv))

        yield {
            'db': g.groups()[0],
            'tb': g.groups()[1],
            'pri': ','.join(validate_privileges(g.groups()[2])),
        }

    elif isinstance(priv, dict):
        for k, v in priv.items():
            if isinstance(k, basestring):
                db, table = k.split('.')

            else:
                db, table = k

            yield {
                'db': db,
                'tb': table,
                'pri': ','.join(validate_privileges(v)),
            }

    else:
        raise ValueError('invalid privileges: expected str or dict, but got: {t}'.format(t=type(priv)))


def _normalize_users(users):
    rst = []
    for user in users:
        username = user.get('name') or ''
        host = user.get('host') or '%'
        pwd = user.get('password')
        state = user.get('state') or 'present'

        for p in _normalize_priv(user.get('priv')):
            fmt_argkw = {
                'pri': p['pri'],
                'db': p['db'],
                'tb': p['tb'],
                'u': username,
                'h': host,
            }
            create_sql = 'CREATE USER IF NOT EXISTS "{u}"@"{h}"'.format(u=username, h=host)
            if create_sql not in rst:
                rst.append(create_sql)

            if state == 'present':
                sql = 'GRANT {pri} ON {db}.{tb} TO "{u}"@"{h}"'.format(**fmt_argkw)

            elif state == 'absent':
                sql = 'REVOKE {pri} ON {db}.{tb} FROM "{u}"@"{h}"'.format(**fmt_argkw)

            else:
                raise ValueError('invalid state: {s} not in (present, absent)'.format(s=state))

            if sql not in rst:
                rst.append(sql)

            if pwd is None:
                continue

            pwd_sql = 'ALTER USER "{u}"@"{h}" IDENTIFIED BY "{p}"'.format(
                u=username, h=host, p=pwd)

            if pwd_sql not in rst:
                rst.append(pwd_sql)

    return rst


def query_by_jinja2(conn_argkw, jinja2_argkw):
    func, call_argkw = _get_query_func(conn_argkw)
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


def setup_user(conn_argkw, users):
    func, call_argkw = _get_query_func(conn_argkw)
    sqls = _normalize_users(users)

    for sql in sqls:
        call_argkw['sql'] = sql
        func(**call_argkw)

    call_argkw['sql'] = 'FLUSH PRIVILEGES'
    func(**call_argkw)
