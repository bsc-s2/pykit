import os
import sys
import time
import unittest

from pykit import redisutil
from pykit import utdocker
from pykit import ututil
from pykit import threadutil

dd = ututil.dd

redis_tag = 'daocloud.io/redis:3.2.3'

redis_port = 6379


class TestRedis(unittest.TestCase):

    def setUp(self):

        self.containers = [
            ('redis-0', redis_tag, '192.168.52.40'),
            ('redis-1', redis_tag, '192.168.52.41'),
        ]

        # for single redis cases:
        self.docker_name = 'redis-0'
        self.ip = '192.168.52.40'
        self.is_child = False

        utdocker.create_network()

        for args in self.containers:
            utdocker.start_container(*(args + ('',)))
            dd('started redis in docker: ' + repr(args))

            redisutil.wait_serve((args[2], redis_port))

        self.rcl = redisutil.get_client((self.ip, redis_port))

    def tearDown(self):

        # do not tear down in child process
        if self.is_child:
            return

        for args in self.containers:
            dd('remove_container: ' + args[0])
            utdocker.remove_container(args[0])

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
            rcl = redisutil.get_client((self.ip, redis_port))
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
            self.rcl = redisutil.get_client((self.ip, redis_port))

        # for both parent and child process
        for i in range(n):
            self.rcl.hset(hname, 'x' + str(i),
                          'foobarjfkdslafjdasklfdjsaklfdsa' + str(i))
            self.rcl.hget(hname, 'x' + str(i - 1))

            if i % 1024 == 0:
                dd('pid:', os.getpid(), ' finished ', i, ' set/get')

        if pid == 0:
            # child
            self.is_child = True
            child_exit()
        else:
            # parent
            os.waitpid(pid, 0)
            dd('child pid quit: ' + repr(pid))

        # no error raised with 2 process hget/hset, it is ok

    def test_2_ip_port(self):
        rcl = []
        for name, tag, ip in self.containers:
            rcl.append(redisutil.get_client((ip, redis_port)))

        rcl[0].hset('foo', 'foo', '100')
        rcl[1].hset('foo', 'foo', '101')

        rst = rcl[0].hget('foo', 'foo')
        dd('rst got from first redis:', rst)

        self.assertEqual('100', rst)

    def test_normalize_ip_port(self):

        self.assertEqual(('127.0.0.1', 1234),
                         redisutil.normalize_ip_port(1234))
        self.assertEqual(('1.2.3.4', 1234),
                         redisutil.normalize_ip_port(('1.2.3.4', 1234)))

    def test_redis_channel(self):

        c = redisutil.RedisChannel((self.ip, redis_port), '/foo', 'client')
        s = redisutil.RedisChannel((self.ip, redis_port), '/foo', 'server')

        rst = s.peek_msg()
        dd('server peek: ', rst)
        self.assertEqual(None, rst)

        c.send_msg('c2s')
        s.send_msg('s2c')

        # peek does not remove message

        for ii in range(2):
            rst = s.peek_msg()
            dd('server peek: ', rst)
            self.assertEqual('c2s', rst)

            rst = c.peek_msg()
            dd('client peek: ', rst)
            self.assertEqual('s2c', rst)

        rst = s.recv_msg()
        dd('server recv: ', rst)
        self.assertEqual('c2s', rst, 'server pop message from client')

        rst = s.peek_msg()
        dd('server peek: ', rst)
        self.assertEqual(None, rst, 'no more message in channel')

        # recv_last_msg

        for ii in range(10):
            s.send_msg('s2c' + str(ii))

        rst = c.recv_last_msg()
        dd('client recv last:', rst)
        self.assertEqual('s2c9', rst)

        rst = c.peek_msg()
        self.assertEqual(
            None, rst, 'all messages should have been read, after recv_last_msg()')

    def test_list_redis_channel(self):

        ca = redisutil.RedisChannel((self.ip, redis_port), '/foo/a', 'client')
        sb = redisutil.RedisChannel((self.ip, redis_port), '/foo/b', 'server')

        rst = ca.list_channel('/foo/')
        dd('before write, list_channel:', rst)
        self.assertEqual([], rst, 'can not list list before any message sent')

        ca.send_msg(1)
        sb.send_msg(2)

        rst = ca.list_channel('/foo/')
        dd('after write, list_channel:', rst)
        self.assertEqual(['/foo/a', '/foo/b'], rst)

        # empty channel then channel can not be seen.
        redisutil.RedisChannel((self.ip, redis_port),
                               '/foo/a', 'server').recv_msg()
        redisutil.RedisChannel((self.ip, redis_port),
                               '/foo/b', 'client').recv_msg()

        rst = ca.list_channel('/foo/')
        self.assertEqual([], rst)

    def test_tuple_channel(self):

        c = redisutil.RedisChannel((self.ip, redis_port), '/foo/a', 'client')
        s = redisutil.RedisChannel(
            (self.ip, redis_port), ('foo', 'a'), 'server')

        c.send_msg(1)
        rst = s.recv_msg()
        dd('server recv:', rst)

        self.assertEqual(1, rst)

    def test_channel_timeout(self):

        ca = redisutil.RedisChannel((self.ip, redis_port), '/foo/a', 'client', timeout=1)
        ca.send_msg(1)
        self.assertEqual(['/foo/a'], ca.list_channel('/foo/'))
        time.sleep(1.5)
        self.assertEqual([], ca.list_channel('/foo/'))

    def test_brecv_message(self):

        c = redisutil.RedisChannel((self.ip, redis_port), '/foo', 'client')
        s = redisutil.RedisChannel((self.ip, redis_port), '/foo', 'server')

        c.send_msg('aa')
        self.assertEqual('aa', s.brecv_msg(timeout=1))
        self.assertEqual(None, s.brecv_msg(timeout=1))

        def _send_msg():
            time.sleep(0.5)
            c.send_msg('bar')

        threadutil.start_daemon_thread(target=_send_msg)
        self.assertEqual('bar', s.brecv_msg(timeout=1))

    def test_brecv_last_message(self):

        c = redisutil.RedisChannel((self.ip, redis_port), '/foo', 'client')
        s = redisutil.RedisChannel((self.ip, redis_port), '/foo', 'server')

        c.send_msg('aa')
        c.send_msg('bb')
        self.assertEqual('bb', s.brecv_last_msg(timeout=1))
        self.assertEqual(None, s.brecv_last_msg(timeout=1))

        def _send_msg():
            time.sleep(0.5)
            c.send_msg('cc')

        threadutil.start_daemon_thread(target=_send_msg)
        self.assertEqual('cc', s.brecv_last_msg(timeout=1))

    def test_rpeek_message(self):

        c = redisutil.RedisChannel((self.ip, redis_port), '/foo', 'client')
        s = redisutil.RedisChannel((self.ip, redis_port), '/foo', 'server')

        self.assertEqual(None, c.rpeek_msg())
        self.assertEqual(None, s.rpeek_msg())

        c.send_msg('c2s1')
        c.send_msg('c2s2')
        s.send_msg('s2c1')
        s.send_msg('s2c2')

        # rpeek does not remove message
        for ii in range(2):
            self.assertEqual('c2s2', s.rpeek_msg())
            self.assertEqual('s2c2', c.rpeek_msg())


def child_exit():

    # to suppress error message caused by sys.exit()
    os.close(0)
    os.close(1)
    os.close(2)

    sys.exit(0)
