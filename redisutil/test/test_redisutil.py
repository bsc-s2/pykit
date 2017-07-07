import os
import subprocess
import time
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

    foo_fn = '/tmp/foo'
    bar_fn = '/tmp/bar'
    pidfn = '/tmp/test_daemonize.pid'

    def _clean(self):

        # kill foo.py and kill bar.py
        # bar.py might be waiting for foo.py to release lock-file.
        try:
            subproc('python2 {b}/foo.py stop'.format(b=this_base))
        except Exception as e:
            print repr(e)

        time.sleep(0.1)

        try:
            subproc('python2 {b}/bar.py stop'.format(b=this_base))
        except Exception as e:
            print repr(e)

        # remove written file

        try:
            os.unlink(self.foo_fn)
        except EnvironmentError as e:
            pass

        try:
            os.unlink(self.bar_fn)
        except EnvironmentError as e:
            pass

    def setUp(self):
        self.redis_name = 'redis-0'
        self.ip = '192.168.52.40'
        utdocker.create_network()
        utdocker.start_container(self.redis_name, redis_tag, self.ip, '')

        self.rcl = redisutil.get_client((self.ip, 6379))
        # self._clean()

    def tearDown(self):
        pass
        # self._clean()

    def test_start(self):

        hname = 'foo'
        rst = self.rcl.hset(hname, 'a', 1)
        dd('hset rst:', rst)

        rst = self.rcl.hget(hname, 'a')
        dd('hget rst:', rst)
