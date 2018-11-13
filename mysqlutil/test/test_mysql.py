#!/usr/bin/env python2
# coding: utf-8

import os

from pykit import ututil
from pykit import mysqlutil
from pykit import mysqlconnpool

from . import base

dd = ututil.dd

mysql_test_user = 'root'
mysql_test_db = 'test'
mysql_test_table = 'test'
this_base = os.path.dirname(os.path.abspath(__file__))


class TestMysql(base.Base):

    def setUp(self):
        super(TestMysql, self).setUp()

        self.addr = {
            'host': base.mysql_test_ip,
            'port': base.mysql_test_port,
            'user': mysql_test_user,
            'passwd': base.mysql_test_password,
        }
        self.conn_pool = mysqlconnpool.make(self.addr)
        self.conn = self.conn_pool.get_conn()

    def test_query_by_jinja2(self):
        create_tb_temp = '''CREATE TABLE `{{ db }}`.`user_{{ sharding_start }}`(
            `_id`      bigint                                      NOT NULL AUTO_INCREMENT,
            `data`     json,
            `username` varchar(64) as (data->"$.username") VIRTUAL NOT NULL,
            `email`    varchar(64) as (data->"$.email")    VIRTUAL NOT NULL,
            PRIMARY KEY (`_id`),
            UNIQUE KEY idx_username (`username`),
            UNIQUE KEY idx_email (`email`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
        '''

        create_tb_temp_path = os.path.join(this_base, 'template.j2')

        cases = (
            {"template": create_tb_temp, 'vars': {'db': 'test', 'sharding_start': 'foo'}},
            {"template_path": create_tb_temp_path, 'vars': {'db': 'test', 'sharding_start': 'foo'}},
        )

        for c in cases:
            # No Exception means success
            for conn in (self.conn, self.conn_pool, self.addr):
                mysqlutil.query_by_jinja2(conn, c)
                mysqlconnpool.conn_query(self.conn, 'DROP TABLE `test`.`user_foo`')

        cases = (
            ('select `ip` from `{{ db }}`.`{{ tb }}`', {'db': 'test', 'tb': 'errlog'}),
        )

        for temp, vars_ in cases:
            argkv = {'template': temp, 'vars': vars_}

            for conn in (self.conn, self.conn_pool, self.addr):
                rst = mysqlutil.query_by_jinja2(conn, argkv)
                self.assertGreater(len(rst), 0)
                self.assertIn('ip', rst[0])

        self.assertRaises(TypeError, mysqlutil.query_by_jinja2, 'foo', {})
        self.assertRaises(ValueError, mysqlutil.query_by_jinja2, self.conn, {})
