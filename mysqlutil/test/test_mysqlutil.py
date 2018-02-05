#!/usr/bin/env python2
# coding: utf-8

import time
import unittest

import docker

from pykit import mysqlconnpool
from pykit import mysqlutil
from pykit import proc
from pykit import ututil

dd = ututil.dd

mysql_test_password = '123qwe'
mysql_test_port = 3306
mysql_test_user = 'root'
mysql_test_name = 'mysql_test'
mysql_test_tag = 'test-mysql:0.0.1'


class TestMysqlutil(unittest.TestCase):

    def test_scan_index(self):

        mysql_ip = start_mysql_server()

        addr = {
            'host': mysql_ip,
            'port': mysql_test_port,
            'user': mysql_test_user,
            'passwd': mysql_test_password,
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
            ([['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {'left_open': True, 'limit': 3, 'index_name': 'idx_time__id'},
             ('12', '18', '20', ),

             'test all kwargs',
            ),
        )

        try:
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

                        self.assertEqual(rr[0], rst_expect[i])

                    self.assertEqual(len(rst_expect), i+1)
        finally:
            stop_mysql_server()

        error_cases = (
            ([addr, table, result_fields, ['service', 'ip', '_id'], ['common0', '127.0.0.2']],
             {},
             mysqlutil.IndexNotPairs,

             'test index_fields amount greater than index_values',
             ),
            ([addr, table, result_fields, ['service', 'ip'], ['common0', '127.0.0.2', '13']],
             {},
             mysqlutil.IndexNotPairs,

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

    def test_sql_scan_index(self):

        table = 'errlog'

        cases = (
            ([['_id'], ['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {},
             'SELECT `_id` FROM `errlog` FORCE INDEX (`idx_service_ip__id`) '
             'WHERE `errlog`.`service` = "common0" AND `errlog`.`ip` = "127.0.0.1" '
             'AND `errlog`.`_id` >= "8" LIMIT 1024',

             'test common',
            ),
            ([['_id', 'ip'], ['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {'left_open': True},
             'SELECT `_id`, `ip` FROM `errlog` FORCE INDEX (`idx_service_ip__id`) '
             'WHERE `errlog`.`service` = "common0" AND `errlog`.`ip` = "127.0.0.1" '
             'AND `errlog`.`_id` > "8" LIMIT 1024',

             'test left_open',
            ),
            ([[], ['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {'limit': 3},
             'SELECT * FROM `errlog` FORCE INDEX (`idx_service_ip__id`) '
             'WHERE `errlog`.`service` = "common0" AND `errlog`.`ip` = "127.0.0.1" '
             'AND `errlog`.`_id` >= "8" LIMIT 3',

             'test limit',
            ),
            ([['_id'], ['service', 'ip', '_id'], ['common0', '127.0.0.2']],
             {},
             'SELECT `_id` FROM `errlog` FORCE INDEX (`idx_service_ip__id`) '
             'WHERE `errlog`.`service` = "common0" AND `errlog`.`ip` >= "127.0.0.2" LIMIT 1024',

             'test index_fields amount greater than index_values',
            ),
            ([['_id'], ['service', 'ip'], ['common0', '127.0.0.2', '13']],
             {},
             'SELECT `_id` FROM `errlog` FORCE INDEX (`idx_service_ip`) '
             'WHERE `errlog`.`service` = "common0" AND `errlog`.`ip` >= "127.0.0.2" LIMIT 1024',

             'test index_fields amount less than index_values',
            ),
            ([['_id'], ['autolvl', 'service', 'ip', '_id'], ['stable', 'common0', '127.0.0.1', '8']],
             {'index_name': 'idx_service_ip__id'},
             'SELECT `_id` FROM `errlog` FORCE INDEX (`idx_service_ip__id`) '
             'WHERE `errlog`.`autolvl` = "stable" AND `errlog`.`service` = "common0" '
             'AND `errlog`.`ip` = "127.0.0.1" AND `errlog`.`_id` >= "8" LIMIT 1024',

             'test index_name',
            ),
            ([['_id'], [], ['stable', 'common0', '127.0.0.1', '8']],
             {},
             'SELECT `_id` FROM `errlog` '
             'LIMIT 1024',

             'test blank index_fields',
            ),
            ([['_id'], ['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {'left_open': True, 'limit': 5, 'index_name': 'idx_time__id'},
             'SELECT `_id` FROM `errlog` FORCE INDEX (`idx_time__id`) '
             'WHERE `errlog`.`service` = "common0" AND `errlog`.`ip` = "127.0.0.1" '
             'AND `errlog`.`_id` > "8" LIMIT 5',

             'test all kwargs',
            ),
        )

        for args, kwargs, rst_expect, msg in cases:

            dd('msg: ', msg)

            args = [table] + args

            rst = mysqlutil.sql_scan_index(*args, **kwargs)

            dd('rst       : ', rst)
            dd('rst_expect: ', rst_expect)

            self.assertEquals(rst, rst_expect)

    def test_sql_condition_between_shards(self):

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

            ((['id', 'service'], ['10', 'a'], ['10', 'd']),
                ['`id` = "10" AND `service` >= "a" AND `service` < "d"'],
                '2 shard field, 1 same fields'),

            ((['id', 'service'], ['10', 'a'], ['15', 'd']),
                ['`id` = "10" AND `service` >= "a"',
                 '`id` = "15" AND `service` < "d"',
                 '`id` > "10" AND `id` < "15"',
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
                 '`id` = "10" AND `service` = "d" AND `level` < "b2"',
                 '`id` = "10" AND `service` > "a" AND `service` < "d"',
                 ],
                '3 shard fields, 1 same fields'),

            ((['id', 'service', 'level'], ['10', 'a', 'a3'], ['15', 'd', 'b2']),
                ['`id` = "10" AND `service` = "a" AND `level` >= "a3"',
                 '`id` = "10" AND `service` > "a"',
                 '`id` = "15" AND `service` = "d" AND `level` < "b2"',
                 '`id` = "15" AND `service` < "d"',
                 '`id` > "10" AND `id` < "15"',
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
                 '`id` = "15" AND `service` = "d\\\\b" AND `level` < "b\\\'2"',
                 '`id` = "15" AND `service` < "d\\\\b"',
                 '`id` > "10" AND `id` < "15"',
                 ],
                'special characters'),
        )

        for args, rst_expected, msg in cases:
            dd('msg: ', msg)
            dd('expected: ', rst_expected)

            rst = mysqlutil.sql_condition_between_shards(*args)
            dd('rst     : ', rst)

            self.assertEqual(rst, rst_expected)


def docker_does_container_exist(name):

    dcli = _docker_cli()
    try:
        dcli.inspect_container(name)
        return True
    except docker.errors.NotFound:
        return False

def _docker_cli():
    dcli = docker.Client(base_url='unix://var/run/docker.sock')
    return dcli

def start_mysql_server():

    # create docker image by run mysqlutil/test/dep/build_img.sh before test
    if not docker_does_container_exist(mysql_test_name):

        dd('create container: ' + mysql_test_name)
        dcli = _docker_cli()
        dcli.create_container(name=mysql_test_name,
                              environment={
                                  'MYSQL_ROOT_PASSWORD': mysql_test_password,
                              },
                              image=mysql_test_tag,
                              )
        time.sleep(2)

    dd('start mysql: ' + mysql_test_name)
    dcli = _docker_cli()
    dcli.start(container=mysql_test_name)

    dd('get mysql ip inside container')
    rc, out, err = proc.command(
        'docker',
        'run',
        '-i',
        '--link', mysql_test_name + ':mysql',
        '--rm', mysql_test_tag,
        'sh', '-c', 'exec echo "$MYSQL_PORT_3306_TCP_ADDR"',
    )

    ip = out.strip()
    dd('ip: ' + repr(ip))

    return ip

def stop_mysql_server():

    # remove docker image by run mysqlutil/test/dep/rm_imd.sh after test
    dcli = _docker_cli()
    dcli.stop(container=mysql_test_name)
