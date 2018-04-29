#!/usr/bin/env python2
# coding: utf-8

import socket
import subprocess32
import time
import unittest

import docker
import MySQLdb

from pykit import mysqlconnpool
from pykit import ututil
from pykit import utdocker

dd = ututil.dd

mysql_test_ip = '192.168.52.40'
mysql_test_password = '123qwe'
mysql_test_port = 3306
mysql_test_user = 'root'
mysql_test_name = 'mysql_test'
mysql_test_tag = 'daocloud.io/mysql:5.7.13'


class ShellError(Exception):
    pass


class Testmysqlconnpool(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        utdocker.pull_image(mysql_test_tag)

    def setUp(self):

        utdocker.start_container(
                mysql_test_name,
                mysql_test_tag,
                ip=mysql_test_ip,
                env={
                    'MYSQL_ROOT_PASSWORD': mysql_test_password,
                },
                port_bindings={
                    mysql_test_port: mysql_test_port
                }

        )

        addr = (mysql_test_ip, mysql_test_port)

        # some time it takes several seconds to start listening
        for ii in range(40):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.connect(addr)
                break
            except socket.error:
                dd('trying to connect to {0} failed'.format(str(addr)))
                sock.close()
                time.sleep(.4)
        else:
            raise

        self.pool = mysqlconnpool.make({
            'host': mysql_test_ip,
            'port': mysql_test_port,
            'user': mysql_test_user,
            'passwd': mysql_test_password,
        })

    def tearDown(self):
        utdocker.remove_container(mysql_test_name)

    def test_pool_name(self):

        pool = self.pool

        name = '{0}:{1}'.format(mysql_test_ip, mysql_test_port)

        self.assertEqual(name, pool('stat')['name'])

    def test_initial_stat(self):

        pool = self.pool

        dd('pool stat: {0}'.format(pool('stat')))

        self.assertEqual(0, pool('stat')['create'])
        self.assertEqual(0, pool('stat')['pool_get'])
        self.assertEqual(0, pool('stat')['pool_put'])

    def test_get_connection(self):

        pool = self.pool

        with pool() as conn:

            dd(conn)
            dd('pool stat: {0}'.format(pool('stat')))

            self.assertEqual(0, pool('stat')['pool_put'])

        dd('pool stat: {0}'.format(pool('stat')))

        self.assertEqual(1, pool('stat')['create'])
        self.assertEqual(0, pool('stat')['pool_get'])
        self.assertEqual(1, pool('stat')['pool_put'])

    def test_connection_is_working(self):

        pool = self.pool

        with pool() as conn:

            dd(conn)

            conn.query('show databases')
            rst = conn.store_result()
            rst = rst.fetch_row(rst.num_rows())

            databases = [x[0] for x in rst]
            self.assertTrue('mysql' in databases)

    def test_get_connection_twice(self):

        pool = self.pool

        c0 = None
        with pool() as conn:
            c0 = conn

        # the second time do not create new connection
        with pool() as conn:

            self.assertTrue(c0 is conn)

            dd('pool stat: {0}'.format(pool('stat')))

            self.assertEqual(1, pool('stat')['create'])
            self.assertEqual(1, pool('stat')['pool_get'])

        # after put back
        dd('pool stat: {0}'.format(pool('stat')))

        self.assertEqual(2, pool('stat')['pool_put'])

    def test_raise_in_with(self):

        pool = self.pool

        try:
            with pool() as conn:
                dd(conn)
                raise ValueError(1)
        except ValueError:
            pass

        dd('pool stat: {0}'.format(pool('stat')))

        self.assertEqual(1, pool('stat')['create'])
        self.assertEqual(0, pool('stat')['pool_get'])
        self.assertEqual(0, pool('stat')['pool_put'])

    def test_conn_query(self):

        pool = self.pool

        with pool() as conn:
            rst = mysqlconnpool.conn_query(conn, 'show databases')

        dd('databases: {0}'.format(rst))

        databases = [x['Database'] for x in rst]
        self.assertTrue('mysql' in databases)

    def test_query(self):

        pool = self.pool

        rst = pool.query('show databases')

        dd('databases: {0}'.format(rst))

        databases = [x['Database'] for x in rst]
        self.assertTrue('mysql' in databases)

    def test_query_retry(self):

        pool = self.pool

        sql = (
            'set session wait_timeout=1;'
        )
        pool.query(sql)
        pool.query('show variables like "%timeout%";')

        with pool() as conn:
            time.sleep(2)
            with self.assertRaises(MySQLdb.OperationalError):
                print conn.query('show databases')

        # no error raise from above, thus a timed out conn has been left in
        # pool
        stat = pool('stat')
        dd('stat after timeout', stat)
        self.assertEqual(1, stat['create'], 'created 1 conn')

        # use previous conn, timed out and retry.
        pool.query('show databases', retry=1)

        stat = pool('stat')
        dd('stat after retry', stat)
        self.assertEqual(2, stat['create'], 'created another conn for retry')

    def test_query_array_result(self):

        pool = self.pool

        rst = pool.query('show databases', use_dict=False)

        dd('databases: {0}'.format(rst))

        databases = [x[0] for x in rst]
        self.assertTrue('mysql' in databases)

    def test_query_charset(self):

        sql_create_table = ('CREATE TABLE `test`.`q` ( `name` varchar(128) NOT NULL)'
                            ' ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin')

        pool = mysqlconnpool.make({
            'host': mysql_test_ip,
            'port': mysql_test_port,
            'user': mysql_test_user,
            'passwd': mysql_test_password,
            'charset': 'utf8',
        })

        rst = pool.query('CREATE DATABASE `test`')
        dd('create database rst: ', rst)

        rst = pool.query(sql_create_table)
        dd('create table rst: ', rst)

        rst = pool.query('INSERT INTO `test`.`q` (`name`) VALUES ("我")')
        dd('insert rst: ', rst)

        rst = pool.query('SELECT * FROM `test`.`q`')
        dd('select rst: ', rst)

        self.assertEqual(({'name': u'\u6211'},), rst)
