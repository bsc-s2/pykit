#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import mysqlconnpool
from pykit import mysqlutil
from pykit import ututil

from . import base

dd = ututil.dd

mysql_test_user = 'root'
mysql_test_db = 'test'
mysql_test_table = 'errlog'


class TestMysqlScanIndex(base.Base):

    def test_scan_index(self):

        addr = {
            'host': base.mysql_test_ip,
            'port': base.mysql_test_port,
            'user': mysql_test_user,
            'passwd': base.mysql_test_password,
        }

        conns = (addr,
                 mysqlconnpool.make(addr),
                 )

        table = ('test', 'errlog')

        result_fields = ['_id']

        cases = (
            ([['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {},
             ('8', '12', '18', '20', '32', '2', '3', '13', '19', '27', '30', '11', '22', '29', '31', '14',
              '28', '4', '5', '9', '24', '6', '15', '21', '23', '25', '26', '10', '16', '7', '17'),

             'test common',
             ),
            ([['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {'left_open': True},
             ('12', '18', '20', '32', '2', '3', '13', '19', '27', '30', '11', '22', '29', '31', '14',
              '28', '4', '5', '9', '24', '6', '15', '21', '23', '25', '26', '10', '16', '7', '17'),

             'test left_open',
             ),
            ([['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {'limit': 3},
             ('8', '12', '18', ),

             'test limit',
             ),
            ([['autolvl', 'service', 'ip', '_id'], ['stable', 'common0', '127.0.0.1', '8']],
             {'index_name': 'idx_service_ip__id'},
             ('12', '32', '2', '13', '19', '30', '22', '28', '6', '15', '21', '7'),

             'test index_name',
             ),
            ([['service', 'ip', '_id'], ['common0', '127.0.0.1', 8]],
             {'left_open': True, 'limit': 3, 'index_name': 'idx_time__id'},
             ('12', '18', '20', ),

             'test all kwargs',
             ),
        )

        for conn in conns:
            dd('conn: ', conn)

            for args, kwargs, rst_expect, msg in cases:

                args = [conn, table, result_fields] + args
                kwargs['use_dict'] = False

                dd('msg: ', msg)

                rst = mysqlutil.scan_index(*args, **kwargs)

                for i, rr in enumerate(rst):
                    dd('rst:', rr)
                    dd('except: ', rst_expect[i])

                    self.assertEqual(rr[0], long(rst_expect[i]))

                self.assertEqual(len(rst_expect), i+1)

        error_cases = (
            ([addr, table, result_fields, ['service', 'ip', '_id'], ['common0', '127.0.0.2']],
             {},
             mysqlutil.InvalidLength,

             'test index_fields amount greater than index_values',
             ),
            ([addr, table, result_fields, ['service', 'ip'], ['common0', '127.0.0.2', '13']],
             {},
             mysqlutil.InvalidLength,

             'test index_fields amount less than index_values',
             ),
            (['addr', table, result_fields, ['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {},
             mysqlutil.ConnectionTypeError,

             'test conn type error',
             ),
        )

        for args, kwargs, error, msg in error_cases:
            dd('msg: ', msg)

            try:
                rst = mysqlutil.scan_index(*args, **kwargs)
            except error as e:
                self.assertEqual(type(e), error)

    def test_make_sharding(self):

        db = mysql_test_db
        table = mysql_test_table
        conn = {
            'host': base.mysql_test_ip,
            'port': base.mysql_test_port,
            'user': mysql_test_user,
            'passwd': base.mysql_test_password,
        }

        def shard_maker(shard):

            new_shard = [str(x) for x in shard]
            new_shard += ['', '', '']

            return tuple(new_shard[:3])

        cases = (
            (
                {
                    "shard_fields": ('service', 'ip', '_id'),
                    "start": ['common0', '', ''],
                    "number_per_shard": 10,
                    "tolerance_of_shard": 1,
                    "shard_maker": tuple,
                },
                {
                    'total': 32,
                    'number': [10, 10, 10, 2],
                    'shard': [('common0', '', ''), ('common0', '127.0.0.3', 27L),
                              ('common2', '127.0.0.1'), ('common4', '127.0.0.1', 7L)],
                },
            ),

            (
                {
                    "shard_fields": ('service', 'ip', '_id'),
                    "start": ['common0', '127.0.0.3', '27'],
                    "number_per_shard": 10,
                    "tolerance_of_shard": 1,
                },
                {
                    'total': 22,
                    'number': [10, 10, 2],
                    'shard': [['common0', '127.0.0.3', '27'],
                              ['common2', '127.0.0.1'], ['common4', '127.0.0.1', 7L]],
                },
            ),

            (
                {
                    "shard_fields": ('service', 'ip', '_id'),
                    "start": ['common0', '', ''],
                    "number_per_shard": 10,
                    "tolerance_of_shard": 1,
                    "shard_maker": shard_maker,
                },
                {
                    'total': 32,
                    'number': [10, 10, 10, 2],
                    'shard': [('common0', '', ''), ('common0', '127.0.0.3', '27'),
                              ('common2', '127.0.0.1', ''), ('common4', '127.0.0.1', '7')],
                },
            ),

            (
                {
                    "shard_fields": ('service', 'ip', '_id'),
                    "start": ['common0', '', ''],
                    "number_per_shard": 15,
                    "tolerance_of_shard": 2,
                    "shard_maker": shard_maker,
                },
                {
                    'total': 32,
                    'number': [15, 15, 2],
                    'shard': [('common0', '', ''), ('common1', '127.0.0.1', '31'), ('common4', '', '')],
                },
            ),

            (
                {
                    "shard_fields": ('time', '_id'),
                    "start": ['201706060600', '1'],
                    "number_per_shard": 10,
                    "tolerance_of_shard": 1,
                },
                {
                    'total': 32,
                    'number': [10, 10, 10, 2],
                    'shard': [['201706060600', '1'], [201706060610L,], [201706060620L,],
                              [201706060630L,]],
                },
            ),
        )

        for kwargs, expected in cases:

            kwargs['db'] = db
            kwargs['table'] = table
            kwargs['conn'] = conn

            dd('expected: ', expected)
            result = mysqlutil.make_sharding(**kwargs)
            dd('result  : ', result)
            self.assertEqual(result, expected)


class TestMysqlutil(unittest.TestCase):

    def test_make_index_scan_sql(self):

        table = 'errlog'

        cases = (
            ([['_id'], ['service', 'ip', '_id'], ['common0', '127.0.0.1', 8]],
             {},
             'SELECT `_id` FROM `errlog` FORCE INDEX (`idx_service_ip__id`) '
             'WHERE `service` = "common0" AND `ip` = "127.0.0.1" AND `_id` >= "8" LIMIT 1024;',

             'test common',
             ),
            ([['_id', 'ip'], ['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {'left_open': True},
             'SELECT `_id`, `ip` FROM `errlog` FORCE INDEX (`idx_service_ip__id`) '
             'WHERE `service` = "common0" AND `ip` = "127.0.0.1" AND `_id` > "8" LIMIT 1024;',

             'test left_open',
             ),
            ([None, ['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {'limit': 3},
             'SELECT * FROM `errlog` FORCE INDEX (`idx_service_ip__id`) '
             'WHERE `service` = "common0" AND `ip` = "127.0.0.1" AND `_id` >= "8" LIMIT 3;',

             'test limit',
             ),
            ([['_id'], ['autolvl', 'service', 'ip', '_id'], ['stable', 'common0', '127.0.0.1', '8']],
             {'index_name': 'idx_service_ip__id'},
             'SELECT `_id` FROM `errlog` FORCE INDEX (`idx_service_ip__id`) '
             'WHERE `autolvl` = "stable" AND `service` = "common0" AND `ip` = "127.0.0.1" '
             'AND `_id` >= "8" LIMIT 1024;',

             'test index_name',
             ),
            ([['_id'], None, ['stable', 'common0', '127.0.0.1', '8']],
             {},
             'SELECT `_id` FROM `errlog` LIMIT 1024;',

             'test blank index_fields',
             ),
            ([['_id'], ['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {'left_open': True, 'limit': 5, 'index_name': 'idx_time__id'},
             'SELECT `_id` FROM `errlog` FORCE INDEX (`idx_time__id`) '
             'WHERE `service` = "common0" AND `ip` = "127.0.0.1" AND `_id` > "8" LIMIT 5;',

             'test all kwargs',
             ),
        )

        for args, kwargs, rst_expect, msg in cases:

            dd('msg: ', msg)
            dd('rst_expect: ', rst_expect)

            args = [table] + args

            rst = mysqlutil.make_index_scan_sql(*args, **kwargs)

            dd('rst       : ', rst)

            self.assertEquals(rst, rst_expect)

    def test_make_insert_sql(self):

        cases = (
            (
                mysql_test_table,
                ['common1', '127.0.0.3', '3'],
                None,

                'INSERT INTO `errlog` VALUES ("common1", "127.0.0.3", "3");',
            ),

            (
                mysql_test_table,
                ['common0', '127.0.0.4', 2],
                ['service', 'ip', '_id'],

                'INSERT INTO `errlog` (`service`, `ip`, `_id`) '
                'VALUES ("common0", "127.0.0.4", "2");',
            ),

            (
                (mysql_test_db, mysql_test_table),
                ['common2', '127.0.0.3', '4'],
                None,

                'INSERT INTO `test`.`errlog` VALUES ("common2", "127.0.0.3", "4");',
            ),

            (
                (mysql_test_db, mysql_test_table),
                ['common"三"', '127.0.0.3', '\\"4'],
                None,

                'INSERT INTO `test`.`errlog` VALUES ("common\\\"三\\\"", "127.0.0.3", "\\\\\\"4");',
            ),
        )

        for table, values, fields, expected in cases:

            dd('expected: ', expected)
            rst = mysqlutil.make_insert_sql(table, values, fields)
            dd('result:   ', rst)

            self.assertEqual(expected, rst)

    def test_make_select_sql(self):

        cases = (
            (
                mysql_test_table,
                ['_id'],
                ['service', 'ip', '_id'],
                ['common0', '127.0.0.1', 8],
                {},
                'SELECT `_id` FROM `errlog` WHERE `service` = "common0" AND `ip` = "127.0.0.1" '
                'AND `_id` = "8";',
            ),

            (
                (mysql_test_db, mysql_test_table),
                ['_id', 'ip'],
                ['service', 'ip', '_id'],
                ['common0', '127.0.0.1', '8'],
                {
                    'limit': 1024,
                },

                'SELECT `_id`, `ip` FROM `test`.`errlog` WHERE `service` = "common0" '
                'AND `ip` = "127.0.0.1" AND `_id` = "8" LIMIT 1024;',
            ),

            (
                mysql_test_table,
                None,
                ['service', 'ip', '_id'],
                ['common0', '127.0.0.1', '8'],
                {
                    'limit': 3,
                    'force_index': 'idx_service_ip__id',
                },

                'SELECT * FROM `errlog` FORCE INDEX (`idx_service_ip__id`) '
                'WHERE `service` = "common0" AND `ip` = "127.0.0.1" AND `_id` = "8" LIMIT 3;',
            ),

            (
                mysql_test_table,
                ['_id'],
                ['service', 'ip', '_id'],
                ['common0', '127.0.0.1', '8'],
                {
                    'limit': 3,
                    'force_index': 'idx_service_ip',
                    'operator': '>=',
                },

                'SELECT `_id` FROM `errlog` FORCE INDEX (`idx_service_ip`) '
                'WHERE `service` = "common0" AND `ip` = "127.0.0.1" AND `_id` >= "8" LIMIT 3;',
            ),

            (
                mysql_test_table,
                ['_id'],
                None,
                None,
                {},

                'SELECT `_id` FROM `errlog`;',
            ),

            (
                mysql_test_table,
                ['_id'],
                ['service', 'ip', '_id'],
                ['common"三"', '127.0.0.1', '\\\'8'],
                {
                    'limit': 3,
                    'force_index': 'idx_service_ip',
                    'operator': '>=',
                },

                'SELECT `_id` FROM `errlog` FORCE INDEX (`idx_service_ip`) '
                'WHERE `service` = "common\\\"三\\\"" AND `ip` = "127.0.0.1" '
                'AND `_id` >= "\\\\\\\'8" LIMIT 3;',
            ),
        )

        for table, result_fields, index, index_values, kwargs, expected in cases:

            dd('expected: ', expected)
            rst = mysqlutil.make_select_sql(
                table, result_fields, index, index_values, **kwargs)
            dd('result:   ', rst)

            self.assertEqual(expected, rst)

    def test_make_update_sql(self):

        cases = (
            (
                mysql_test_table,
                {
                    '_id': '0',
                    'time': '042718',
                },
                ['service', 'ip', '_id'],
                ['common0', '127.0.0.1', 8],
                {},
                'UPDATE `errlog` SET `_id` = "0", `time` = "042718" '
                'WHERE `service` = "common0" AND `ip` = "127.0.0.1" AND `_id` = "8";',
            ),

            (
                (mysql_test_db, mysql_test_table),
                {
                    '_id': '0',
                    'time': '042718',
                },
                ['service', 'ip', '_id'],
                ['common0', '127.0.0.1', '8'],
                {
                    'limit': 1,
                },
                'UPDATE `test`.`errlog` SET `_id` = "0", `time` = "042718" '
                'WHERE `service` = "common0" AND `ip` = "127.0.0.1" AND `_id` = "8" LIMIT 1;',
            ),

            (
                (mysql_test_db, mysql_test_table),
                {
                    '_id': '0',
                    'time': '042718',
                },
                None,
                None,
                {
                    'limit': 1,
                },
                'UPDATE `test`.`errlog` SET `_id` = "0", `time` = "042718" LIMIT 1;',
            ),

            (
                (mysql_test_db, mysql_test_table),
                {
                    '_id': '0',
                    'time': '04\"27\'18',
                },
                ['service', 'ip', '_id'],
                ['common"三"', '127.0.0.1', '8'],
                {
                    'limit': 1,
                },
                'UPDATE `test`.`errlog` SET `_id` = "0", `time` = "04\\\"27\\\'18" '
                'WHERE `service` = "common\\\"三\\\"" AND `ip` = "127.0.0.1" AND `_id` = "8" LIMIT 1;',
            ),
        )

        for table, values, index, index_values, kwargs, expected in cases:

            dd('expected: ', expected)
            rst = mysqlutil.make_update_sql(
                table, values, index, index_values, **kwargs)
            dd('result:   ', rst)

            self.assertEqual(expected, rst)

    def test_make_delete_sql(self):

        cases = (
            (
                mysql_test_table,
                ['service', 'ip', '_id'],
                ['common0', '127.0.0.1', 8],
                {},
                'DELETE FROM `errlog` WHERE `service` = "common0" AND `ip` = "127.0.0.1" '
                'AND `_id` = "8";',
            ),

            (
                (mysql_test_db, mysql_test_table),
                ['service', 'ip', '_id'],
                ['common0', '127.0.0.1', '8'],
                {
                    'limit': 1,
                },

                'DELETE FROM `test`.`errlog` WHERE `service` = "common0" '
                'AND `ip` = "127.0.0.1" AND `_id` = "8" LIMIT 1;',
            ),

            (
                mysql_test_table,
                None,
                None,
                {
                    'limit': 1,
                },

                'DELETE FROM `errlog` LIMIT 1;',
            ),

            (
                mysql_test_table,
                ['service', 'ip', '_id'],
                ['common"三"', '127.0.0.1', '\\\'8'],
                {
                    'limit': 1,
                },

                'DELETE FROM `errlog` '
                'WHERE `service` = "common\\\"三\\\"" AND `ip` = "127.0.0.1" '
                'AND `_id` = "\\\\\\\'8" LIMIT 1;',
            ),
        )

        for table, index, index_values, kwargs, expected in cases:

            dd('expected: ', expected)
            rst = mysqlutil.make_delete_sql(
                table, index, index_values, **kwargs)
            dd('result:   ', rst)

            self.assertEqual(expected, rst)

    def test_make_sql_range_conditions(self):

        cases = (
            ((['id'], ['10']),
                ['`id` >= "10"'],
                '1 shard field, no end shard'),

            ((['id'], ['10'], ['15']),
                ['`id` >= "10" AND `id` < "15"'],
                '1 shard field normal'),

            ((['id', 'service'], ['10', 'a']),
                ['`id` = "10" AND `service` >= "a"',
                 '`id` > "10"',
                 ],
                '2 shard fields, no end shard'),

            ((['id', 'service'], [10, 'a'], [10, 'd']),
                ['`id` = "10" AND `service` >= "a" AND `service` < "d"'],
                '2 shard field, 1 same fields'),

            ((['id', 'service'], ['10', 'a'], ['15', 'd']),
                ['`id` = "10" AND `service` >= "a"',
                 '`id` > "10" AND `id` < "15"',
                 '`id` = "15" AND `service` < "d"',
                 ],
                '2 shard fields normal'),

            ((['id', 'service', 'level'], ['10', 'a', 'a3']),
                ['`id` = "10" AND `service` = "a" AND `level` >= "a3"',
                 '`id` = "10" AND `service` > "a"',
                 '`id` > "10"',
                 ],
                '3 shard fields, no end shard'),

            ((['id', 'service', 'level'], ['10', 'a', 'a3'], ['10', 'a', 'b2']),
                ['`id` = "10" AND `service` = "a" AND `level` >= "a3" AND `level` < "b2"'],
                '3 shard fields, 2 same fields'),

            ((['id', 'service', 'level'], ['10', 'a', 'a3'], ['10', 'd', 'b2']),
                ['`id` = "10" AND `service` = "a" AND `level` >= "a3"',
                 '`id` = "10" AND `service` > "a" AND `service` < "d"',
                 '`id` = "10" AND `service` = "d" AND `level` < "b2"',
                 ],
                '3 shard fields, 1 same fields'),

            ((['id', 'service', 'level'], ['10', 'a', 'a3'], ['15', 'd', 'b2']),
                ['`id` = "10" AND `service` = "a" AND `level` >= "a3"',
                 '`id` = "10" AND `service` > "a"',
                 '`id` > "10" AND `id` < "15"',
                 '`id` = "15" AND `service` < "d"',
                 '`id` = "15" AND `service` = "d" AND `level` < "b2"',
                 ],
                '3 shard fields normal'),

            ((['id', 'service', 'level'], ['15', 'd', 'b2'], ['10', 'a', 'a3']),
                [],
                'start > end'),

            ((['id', 'service', 'level'], ['10', 'a', 'a3'], ['10', 'a', 'a3']),
                [],
                'start == end'),

            ((['id', 'service', 'level'], ['10', 'a"c', 'a"3"'], ['15', 'd\\b', 'b\'2']),
                ['`id` = "10" AND `service` = "a\\\"c" AND `level` >= "a\\\"3\\\""',
                 '`id` = "10" AND `service` > "a\\\"c"',
                 '`id` > "10" AND `id` < "15"',
                 '`id` = "15" AND `service` < "d\\\\b"',
                 '`id` = "15" AND `service` = "d\\\\b" AND `level` < "b\\\'2"',
                 ],
                'special characters'),
        )

        for args, rst_expected, msg in cases:
            dd('msg: ', msg)
            dd('expected: ', rst_expected)

            rst = mysqlutil.make_sql_range_conditions(*args)
            dd('rst     : ', rst)

            self.assertEqual(rst, rst_expected)

    def test_make_range_mysqldump_cmd(self):

        conn = {
            'host': '127.0.0.1',
            'user': 'root',
            'passwd': 'password',
            'port': 3306,
        }

        conn_special = {
            'host': '127.0.0.1',
            'user': 'root"1',
            'passwd': 'pass\'word',
            'port': 3306,
        }

        db = 'mysql'
        table = 'key'
        table_special = 'key"00"'

        cases = (
            ((['id', 'service'], conn, db, table, ['/tmp', 'key.sql'], ['/usr', 'bin', 'mysqldump'],
                [10, 'a'], [15, 'd']),
                ("'/usr/bin/mysqldump' --host='127.0.0.1' --port='3306' --user='root' --password='password' " +
                 "'mysql' 'key' -w '" +
                 "(`id` = \"10\" AND `service` >= \"a\") OR " +
                 "(`id` > \"10\" AND `id` < \"15\") OR " +
                 "(`id` = \"15\" AND `service` < \"d\")" +
                 "' > '/tmp/key.sql'"),
                'test normal'
             ),

            ((['id', 'service'], conn, db, table, '/tmp/key.sql', ['/usr', 'bin', 'mysqldump'],
                ['10', 'a'], ['15', 'd']),
                ("'/usr/bin/mysqldump' --host='127.0.0.1' --port='3306' --user='root' --password='password' " +
                 "'mysql' 'key' -w '" +
                 "(`id` = \"10\" AND `service` >= \"a\") OR " +
                 "(`id` > \"10\" AND `id` < \"15\") OR " +
                 "(`id` = \"15\" AND `service` < \"d\")" +
                 "' > '/tmp/key.sql'"),
                'test string path_dump_to'
             ),

            ((['id', 'service'], conn, db, table, ['/tmp', 'key.sql'], '/usr/bin/mysqldump',
                ['10', 'a'], ['15', 'd']),
                ("'/usr/bin/mysqldump' --host='127.0.0.1' --port='3306' --user='root' --password='password' " +
                 "'mysql' 'key' -w '" +
                 "(`id` = \"10\" AND `service` >= \"a\") OR " +
                 "(`id` > \"10\" AND `id` < \"15\") OR " +
                 "(`id` = \"15\" AND `service` < \"d\")" +
                 "' > '/tmp/key.sql'"),
                'test string mysqldump path'
             ),

            ((['id', 'service'], conn, db, table, ['/tmp', 'key.sql'], ['/usr', 'bin', 'mysqldump'],
                ['10', 'a']),
                ("'/usr/bin/mysqldump' --host='127.0.0.1' --port='3306' --user='root' --password='password' " +
                 "'mysql' 'key' -w '" +
                 "(`id` = \"10\" AND `service` >= \"a\") OR " +
                 "(`id` > \"10\")" +
                 "' > '/tmp/key.sql'"),
                'test no end shard'
             ),

            ((['id', 'service'], conn, db, table, ['/tmp', 'key.sql'], ['/usr', 'bin', 'mysqldump'],
                ['10', 'a"'], ['15', 'd"3"']),
                ("'/usr/bin/mysqldump' --host='127.0.0.1' --port='3306' --user='root' --password='password' " +
                 "'mysql' 'key' -w '"
                 "(`id` = \"10\" AND `service` >= \"a\\\"\") OR " +
                 "(`id` > \"10\" AND `id` < \"15\") OR " +
                 "(`id` = \"15\" AND `service` < \"d\\\"3\\\"\")" +
                 "' > '/tmp/key.sql'"),
                'test special characters in shards'
             ),

            ((['id', 'service'], conn_special, db, table_special, ['/tmp', 'key.sql'], ['/usr', 'bin', 'mysqldump'],
                ['10', 'a'], ['15', 'd']),
                ("'/usr/bin/mysqldump' --host='127.0.0.1' --port='3306' --user='root\"1' --password='pass\\\'word' " +
                 "'mysql' 'key\"00\"' -w '" +
                 "(`id` = \"10\" AND `service` >= \"a\") OR " +
                 "(`id` > \"10\" AND `id` < \"15\") OR " +
                 "(`id` = \"15\" AND `service` < \"d\")" +
                 "' > '/tmp/key.sql'"),
                'test special characters in dbinfo'
             ),
        )

        for args, rst_expected, msg in cases:
            dd('msg: ', msg)
            dd('expected: ', rst_expected)
            rst = mysqlutil.make_range_mysqldump_cmd(*args)
            dd('rst     : ', rst)

            self.assertEquals(rst_expected, rst)
