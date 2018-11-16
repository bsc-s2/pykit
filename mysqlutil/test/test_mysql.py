#!/usr/bin/env python2
# coding: utf-8

import os
import MySQLdb
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

    def test_setup_user(self):
        # test grant
        cases = (
            (
                "'foo'@'127.0.0.1'",
                [{"name": 'foo', "host": "127.0.0.1", "priv": "test.errlog:INSERT", "state": "present"}],
                ({'Grants for foo@127.0.0.1': "GRANT USAGE ON *.* TO 'foo'@'127.0.0.1'"},
                 {'Grants for foo@127.0.0.1': "GRANT INSERT ON `test`.`errlog` TO 'foo'@'127.0.0.1'"}),
            ),

            (
                "'foo'@'127.0.0.1'",
                [{"name": 'foo', "host": "127.0.0.1", "priv": "test.errlog:INSERT,UPDATE"}],
                ({'Grants for foo@127.0.0.1': "GRANT USAGE ON *.* TO 'foo'@'127.0.0.1'"},
                 {'Grants for foo@127.0.0.1': "GRANT INSERT, UPDATE ON `test`.`errlog` TO 'foo'@'127.0.0.1'"}),
            ),

            (
                "'foo'@'127.0.0.1'",
                [{"name": 'foo', "host": "127.0.0.1", "priv": {"test.errlog": ['INSERT']}}],
                ({'Grants for foo@127.0.0.1': "GRANT USAGE ON *.* TO 'foo'@'127.0.0.1'"},
                 {'Grants for foo@127.0.0.1': "GRANT INSERT ON `test`.`errlog` TO 'foo'@'127.0.0.1'"}),
            ),

            (
                "'foo'@'127.0.0.1'",
                [{"name": 'foo', "host": "127.0.0.1", "priv": {"test.errlog": ['INSERT', "SELECT"]}}],
                ({'Grants for foo@127.0.0.1': "GRANT USAGE ON *.* TO 'foo'@'127.0.0.1'"},
                 {'Grants for foo@127.0.0.1': "GRANT SELECT, INSERT ON `test`.`errlog` TO 'foo'@'127.0.0.1'"}),
            ),

            (
                "'foo'@'127.0.0.1'",
                [{"name": 'foo', "host": "127.0.0.1", "priv": "test.errlog:INSERT"},
                 {"name": 'foo', "host": "127.0.0.1", "priv": "test.errlog:UPDATE"}],
                ({'Grants for foo@127.0.0.1': "GRANT USAGE ON *.* TO 'foo'@'127.0.0.1'"},
                 {'Grants for foo@127.0.0.1': "GRANT INSERT, UPDATE ON `test`.`errlog` TO 'foo'@'127.0.0.1'"}),
            ),

            (
                "'foo'@'127.0.0.1'",
                [{"name": 'foo', "host": "127.0.0.1", "priv": {"test.errlog": ['INSERT', "SELECT"]}},
                 {"name": 'foo', "host": "127.0.0.1", "priv": {"test.errlog": ['UPDATE']}}],
                ({'Grants for foo@127.0.0.1': "GRANT USAGE ON *.* TO 'foo'@'127.0.0.1'"},
                 {'Grants for foo@127.0.0.1': "GRANT SELECT, INSERT, UPDATE ON `test`.`errlog` TO 'foo'@'127.0.0.1'"}),
            ),

            (
                "'foo'@'127.0.0.1'",
                [{"name": 'foo', "host": "127.0.0.1", "priv": "test.errlog:INSERT,UPDATE"},
                 {"name": 'foo', "host": "127.0.0.1", "priv": "*.*:SELECT"}],
                ({'Grants for foo@127.0.0.1': "GRANT SELECT ON *.* TO 'foo'@'127.0.0.1'"},
                 {'Grants for foo@127.0.0.1': "GRANT INSERT, UPDATE ON `test`.`errlog` TO 'foo'@'127.0.0.1'"}),
            ),

            (
                "foo",
                [{"name": 'foo', "host": "%", "priv": "test.errlog:INSERT", "state": "present"}],
                ({'Grants for foo@%': "GRANT USAGE ON *.* TO 'foo'@'%'"},
                 {'Grants for foo@%': "GRANT INSERT ON `test`.`errlog` TO 'foo'@'%'"}),
            ),

            (
                "foo",
                [{"name": 'foo', "priv": "test.errlog:INSERT"}],
                ({'Grants for foo@%': "GRANT USAGE ON *.* TO 'foo'@'%'"},
                 {'Grants for foo@%': "GRANT INSERT ON `test`.`errlog` TO 'foo'@'%'"}),
            ),

            (
                "'foo'@'127.0.0.1'",
                [{"name": 'foo', "host": "127.0.0.1", "priv": {('test', 'errlog'): ['INSERT', "SELECT"]}}],
                ({'Grants for foo@127.0.0.1': "GRANT USAGE ON *.* TO 'foo'@'127.0.0.1'"},
                 {'Grants for foo@127.0.0.1': "GRANT SELECT, INSERT ON `test`.`errlog` TO 'foo'@'127.0.0.1'"}),
            ),
        )

        for name, c, expected in cases:
            mysqlutil.setup_user(self.addr, c)
            pri = mysqlconnpool.conn_query(self.conn, 'SHOW GRANTS FOR ' + name)
            self.assertEqual(expected, pri)
            mysqlconnpool.conn_query(self.conn, 'DROP USER ' + name)

        # test revoke
        cases = (
            [{"name": 'foo', "priv": "test.errlog:INSERT", 'state': 'absent'}],
            [{"name": 'foo', "priv": {"test.errlog": ["INSERT"]}, 'state': 'absent'}],
            [{"name": 'foo', "priv": {("test", "errlog"): ["INSERT"]}, 'state': 'absent'}],
        )

        pris = [{"name": 'foo', "priv": "test.errlog:SELECT,INSERT,UPDATE"}]
        for c in cases:
            mysqlutil.setup_user(self.conn, pris)
            mysqlutil.setup_user(self.conn, c)
            res = mysqlconnpool.conn_query(self.conn, 'SHOW GRANTS FOR foo')
            expected = ({'Grants for foo@%': "GRANT USAGE ON *.* TO 'foo'@'%'"},
                        {'Grants for foo@%': "GRANT SELECT, UPDATE ON `test`.`errlog` TO 'foo'@'%'"})
            self.assertEqual(expected, res)
            mysqlconnpool.conn_query(self.conn, 'DROP USER foo')

        # test password
        pris = [{"name": 'foo', 'host': '192.168.52.254', 'password': 'abcdef', "priv": "test.errlog:SELECT"}]
        mysqlutil.setup_user(self.conn_pool, pris)
        addr = {
            'host': base.mysql_test_ip,
            'port': base.mysql_test_port,
            'user': 'foo',
            'passwd': 'abcdef',
        }
        pool = mysqlconnpool.make(addr)
        rst = pool.query('SELECT * FROM `test`.`errlog`')
        self.assertGreater(len(rst), 0)

        # wrong password
        addr['passwd'] = '123456'
        pool = mysqlconnpool.make(addr)
        self.assertRaises(MySQLdb.OperationalError, pool.query, 'SELECT * FROM `test`.`errlog`')

        # use another host connect mysql
        pris = [{"name": 'bar', 'host': '10.10.10.10', 'password': 'abcdef', "priv": "test.errlog:SELECT"}]
        mysqlutil.setup_user(self.conn_pool, pris)
        addr['passwd'] = 'abcdef'
        addr['user'] = 'bar'
        pool = mysqlconnpool.make(addr)
        self.assertRaises(MySQLdb.OperationalError, pool.query, 'SELECT * FROM `test`.`errlog`')

        # test Exception
        self.assertRaises(ValueError, mysqlutil.setup_user, self.addr, [{'state': 'xx'}])
        self.assertRaises(ValueError, mysqlutil.setup_user, self.addr, [{'priv': 123}])
        self.assertRaises(ValueError, mysqlutil.setup_user, self.addr, [{'priv': 'db.tb'}])
        self.assertRaises(ValueError, mysqlutil.setup_user, self.addr, [{'priv': 'db.tb:FOO'}])
