import os
import sys
import subprocess
import time
import redis
import unittest

from pykit import redisutil

from pykit import utdocker
from pykit import ututil

dd = ututil.dd

this_base = os.path.dirname(__file__)

redis_tag = 'daocloud.io/redis:3.2.3'


def read_file(fn):
    try:
        with open(fn, 'r') as f:
            cont = f.read()
            return cont
    except EnvironmentError:
        return None


class TestRedis(unittest.TestCase):

    def setUp(self):

        self.docker_name = 'redis-0'
        self.ip = '192.168.52.40'
        self.port = 6379
        self.is_child = False

        utdocker.create_network()
        utdocker.start_container(self.docker_name, redis_tag, self.ip, '')
        dd('started redis in docker')

        # wait for redis to work

        t = time.time() + 5
        while time.time() < t:
            self.rcl = redisutil.get_client((self.ip, self.port))
            try:
                self.rcl.hget('foo', 'foo')
                dd('redis is ready: ' + repr((self.ip, self.port)))
                break
            except redis.ConnectionError as e:
                dd('can not connect to redis: ' + repr((self.ip, self.port)))
                time.sleep(0.1)
                continue
        # os.system('docker ps')

    def tearDown(self):

        # do not tear down in child process
        if self.is_child:
            return

        dd('remove_container: ' + self.docker_name)
        utdocker.remove_container(self.docker_name)

    def test_set_get(self):

        hname = 'foo'

        rst = self.rcl.hset(hname, 'a', '1')
        dd('hset rst:', rst)

        rst = self.rcl.hget(hname, 'a')
        dd('hget rst:', rst)

        self.assertEqual('1', rst)

    def test_recreate_client(self):

        hname = 'foo'

        pid = os.fork()

        dd('my pid:', os.getpid())

        if pid == 0:
            # child
            self.is_child = True
            rcl = redisutil.get_client((self.ip, self.port))
            rcl.hset(hname, 'a', '5')

            child_exit()

        else:
            # parent

            os.waitpid(pid, 0)
            dd('child pid quit: ' + repr(pid))

            rst = self.rcl.hget(hname, 'a')

            dd('redis hget rst:', rst)

            self.assertEqual('5', rst)

    def test_separated_connection_after_fork(self):

        hname = 'foo'

        pid = os.fork()
        dd('my pid:', os.getpid())
        n = 10240

        if pid == 0:
            # child
            self.rcl = redisutil.get_client((self.ip, self.port))

        # for both parent and child process
        for i in range(n):
            self.rcl.hset(hname, 'x' + str(i), 'foobarjfkdslafjdasklfdjsaklfdsa' + str(i))
            self.rcl.hget(hname, 'x' + str(i-1))

            if i % 100 == 0:
                dd(os.getpid(), ' finished ', i, ' set/get')

        if pid == 0:
            # child
            self.is_child = True
            child_exit()
        else:
            # parent
            os.waitpid(pid, 0)
            dd('child pid quit: ' + repr(pid))

        # no error raised with 2 process hget/hset, it is ok


def child_exit():
    # to suppress error message about sys.exit
    os.close(0)
    os.close(1)
    os.close(2)

    sys.exit(0)
