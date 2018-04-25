#!/usr/bin/env python2
# coding: utf-8

import copy
import logging
import Queue

import MySQLdb

logger = logging.getLogger(__name__)


retriable_err = (2006, 2013)


class MysqlConnectionPool(object):

    def __init__(self, conn_argkw, options=None):

        options = options or {}
        options = copy.deepcopy(options)

        self.options = options
        self.queue = Queue.Queue(32)
        self.conn_argkw = conn_argkw
        if 'host' in conn_argkw:
            self.name = '{host}:{port}'.format(**conn_argkw)
        else:
            self.name = '{unix_socket}'.format(**conn_argkw)

        self.stat = {'name': self.name,
                     'create': 0,
                     'pool_get': 0,
                     'pool_put': 0,
                     }

    def __call__(self, action=None):

        if action is None or action == 'get_conn':
            return ConnectionWrapper(self)
        elif action == 'stat':
            return self.stat
        else:
            raise ValueError(action, 'invalid action: ' + repr(action))

    def get_conn(self):

        try:
            conn = self.queue.get(block=False)
            self.stat['pool_get'] += 1
            logger.debug('reuse connection:' + repr(self.stat))
            return conn

        except Queue.Empty:

            conn = new_connection(self.conn_argkw, options=self.options)

            self.stat['create'] += 1
            logger.info('create new connection: ' + repr(self.stat))

            return conn

    def put_conn(self, conn):

        try:
            self.queue.put(conn, block=False)
            self.stat['pool_put'] += 1
            logger.debug('put connection:' + repr(self.stat))

        except Queue.Full:
            conn.close()

    def query(self, sql, use_dict=True, retry=0):

        if retry < 0:
            retry = 0

        retry = int(retry)

        # the first attempt does not count as 'retry'
        for i in range(retry + 1):

            try:
                with self() as conn:
                    return conn_query(conn, sql, use_dict=use_dict)

            except MySQLdb.OperationalError as e:
                if len(e.args) > 0 and e[0] in retriable_err:
                    logger.info(
                        repr(e) + " conn_query error {sql}".format(sql=sql))
                    continue
                else:
                    raise
        else:
            raise


class ConnectionWrapper(object):

    def __init__(self, pool):
        self.pool = pool
        self.conn = None

    def __enter__(self):
        self.conn = self.pool.get_conn()
        return self.conn

    def __exit__(self, errtype, errval, _traceback):

        if errtype is None:
            self.pool.put_conn(self.conn)
            self.conn = None
        else:
            self.conn.close()


def make(conn_argkw, options=None):

    return MysqlConnectionPool(conn_argkw, options=options)


def conn_query(conn, sql, use_dict=True):

    if use_dict:
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
    else:
        cur = conn.cursor()

    cur.execute(sql)
    rst = cur.fetchall()
    cur.close()

    return rst


def new_connection(conn_argkw, options=None):

    # useful arg could be added in future.:
    # conn_argkw.init_command

    options = options or {}

    opt = {
        'autocommit': 1,
    }
    opt.update(options)

    conn = MySQLdb.connect(**conn_argkw)
    for k, v in opt.items():
        conn.query('set {k}={v}'.format(k=k, v=v))

    return conn
