#!/usr/bin/env python2
# coding: utf-8

import socket
import subprocess
import time
import unittest

import docker
import mysqlconnpool

_DEBUG_ = True

mysql_test_password = '123qwe'
mysql_test_port = 3306
mysql_test_user = 'root'
mysql_test_name = 'mysql_test'
mysql_test_tag = 'daocloud.io/mysql:5.7.13'


class ShellError(Exception):
    pass


class Testmysqlconnpool(unittest.TestCase):

    mysql_ip = None

    def setUp(self):

        self.mysql_ip = start_mysql_server()

        addr = (self.mysql_ip, mysql_test_port)

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
            'host': self.mysql_ip,
            'port': mysql_test_port,
            'user': mysql_test_user,
            'passwd': mysql_test_password,
        })

    def tearDown(self):
        stop_mysql_server()

    def test_pool_name(self):

        pool = self.pool

        name = '{0}:{1}'.format(self.mysql_ip, mysql_test_port)

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

    def test_query_array_result(self):

        pool = self.pool

        rst = pool.query('show databases', use_dict=False)

        dd('databases: {0}'.format(rst))

        databases = [x[0] for x in rst]
        self.assertTrue('mysql' in databases)


def start_mysql_server():

    run_shell('service', 'docker', 'start')

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


def stop_mysql_server():

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


def dd(*msg):
    if not _DEBUG_:
        return

    for m in msg:
        print str(m),
    print
