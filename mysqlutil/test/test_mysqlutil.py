#!/usr/bin/env python2
# coding: utf-8

import subprocess
import time
import unittest

import docker
import MySQLdb

from pykit import mysqlutil
from pykit import ututil

dd = ututil.dd

mysql_test_password = '123qwe'
mysql_test_port = 3306
mysql_test_user = 'root'
mysql_test_name = 'mysql_test'
mysql_test_tag = 'test-mysql:0.0.1'


class ShellError(Exception):
    pass


class TestMysqlutil(unittest.TestCase):

    mysql_ip = None

    def setUp(self):

        self.mysql_ip = start_mysql_server()

    def tearDown(self):
        stop_mysql_server()

    def test_scan_index(self):

        addr = {
            'host': self.mysql_ip,
            'port': mysql_test_port,
            'user': mysql_test_user,
            'passwd': mysql_test_password,
        }

        db = 'test'

        table = 'errlog'

        result_fields = ['_id']

        cases = (
            ([['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {},
             ('8', '12', '18', '20', '32', ),
             'test common',
            ),
            ([['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {'left_open': True},
             ('12', '18', '20', '32', ),
             'test left_open',
            ),
            ([['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
             {'limit': 3},
             ('8', '12', '18', ),
             'test limit',
            ),
            ([['service', 'ip', '_id'], ['common0', '127.0.0.2']],
             {},
             ('2', '3', '13', '19', '27', '30', ),
             'test index_fields amount greater than index_values',
            ),
            ([['service', 'ip'], ['common0', '127.0.0.2', '13']],
             {},
             ('2', '3', '13', '19', '27', '30', ),
             'test index_fields amount less than index_values',
            ),
            ([['autolvl', 'service', 'ip', '_id'], ['stable', 'common0', '127.0.0.1', '8']],
             {'index_name': 'idx_service_ip__id'},
             ('12', '32', ),
             'test index_name',
            ),
            ([['service', 'ip', '_id'], ['common0', '127.0.0.1', '8']],
            {'left_open': True, 'limit': 3, 'index_name': 'idx_time__id'},
             ('12', '18', '20', ),
             'test all argkv',
            ),
        )

        for args, argkv, rst_expect, msg in cases:

            args = [addr, db, table, result_fields] + args
            argkv['use_dict'] = False

            dd('msg: ', msg)

            rst = mysqlutil.scan_index(*args, **argkv)

            for i, rr in enumerate(rst):
                dd('rst:', rr)
                dd('except: ', rst_expect[i])

                self.assertEqual(rr[0], rst_expect[i])

            self.assertEqual(len(rst_expect), i+1)

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

             'test all argkv',
            ),
        )

        for args, argkv, rst_expect, msg in cases:

            dd('msg: ', msg)

            args = [table] + args

            rst = mysqlutil.sql_scan_index(*args, **argkv)

            dd('rst       : ', rst)
            dd('rst_expect: ', rst_expect)

            self.assertEquals(rst, rst_expect)

def stop_mysql_server():

    # remove docker image by run mysqlutil/test/dep/rm_imd.sh after test
    dcli = _docker_cli()
    dcli.stop(container=mysql_test_name)

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

def docker_cmd(*args, **argkv):
    args = ['docker'] + list(args)
    return run_shell(*args, **argkv)

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
    rc, out, err = docker_cmd(
        'run',
        '-it',
        '--link', mysql_test_name + ':mysql',
        '--rm', mysql_test_tag,
        'sh', '-c', 'exec echo "$MYSQL_PORT_3306_TCP_ADDR"',
    )

    ip = out.strip()
    dd('ip: ' + repr(ip))

    return ip

def run_shell(*args, **argkv):

    subproc = subprocess.Popen(args,
                               close_fds=True,
                               cwd=None,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, )

    out, err = subproc.communicate()

    subproc.wait()

    if subproc.returncode != 0:
        raise ShellError(subproc.returncode, out, err, args, argkv)

    rst = [subproc.returncode, out, err]

    return rst
