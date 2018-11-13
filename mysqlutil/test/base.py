#!/usr/bin/env python2
# coding: utf-8

import os
import unittest

from pykit import utdocker
from pykit import ututil

mysql_base_tag = 'daocloud.io/mysql:5.7.13'
mysql_test_password = '123qwe'
mysql_test_ip = '192.168.52.40'
mysql_test_port = 3306
mysql_test_name = 'mysql_test'
mysql_test_tag = 'test-mysql:0.0.1'


class Base(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        utdocker.pull_image(mysql_base_tag)

        docker_file_dir = os.path.abspath(os.path.dirname(__file__)) + '/dep'

        utdocker.build_image(mysql_test_tag, docker_file_dir)

    def setUp(self):

        utdocker.create_network()

        utdocker.start_container(
            mysql_test_name,
            mysql_test_tag,
            ip=mysql_test_ip,
            env={
                'MYSQL_ROOT_PASSWORD': mysql_test_password,
            }
        )

        ututil.wait_listening(mysql_test_ip, mysql_test_port)

    def tearDown(self):
        utdocker.remove_container(mysql_test_name)
