import mock
import os
import sys
import time
import unittest
import urlparse

from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer

from pykit import redisutil
from pykit import threadutil
from pykit import utdocker
from pykit import ututil
from pykit import utfjson

dd = ututil.dd

redis_tag = 'daocloud.io/redis:3.2.3'

redis_port = 6379


class TestRedis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        utdocker.pull_image(redis_tag)

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


class TestRedisProxyClient(unittest.TestCase):

    response = {}
    request = {}
    access_key = 'test_accesskey'
    secret_key = 'test_secretkey'

    def setUp(self):
        self.addr = ('127.0.0.1', 22038)

        self.response['http-status'] = 200

        def _start_http_svr():
            self.http_server = HTTPServer(self.addr, HttpHandle)
            self.http_server.serve_forever()

        threadutil.start_daemon_thread(_start_http_svr)
        time.sleep(0.1)

        self.cli = redisutil.RedisProxyClient([self.addr])
        self.n = self.cli.n
        self.w = self.cli.w
        self.r = self.cli.r

    def tearDown(self):
        self.http_server.shutdown()
        self.http_server.server_close()

    def test_send_request_failed(self):
        # close http server
        self.tearDown()

        self.assertRaises(redisutil.SendRequestError, self.cli.get, 'foo')
        self.assertRaises(redisutil.SendRequestError, self.cli.set, 'foo', 'bar')

        self.assertRaises(redisutil.SendRequestError, self.cli.hget, 'foo', 'bar')
        self.assertRaises(redisutil.SendRequestError, self.cli.hset, 'foo', 'bar', 'xx')

    def test_not_found(self):
        self.response['http-status'] = 404
        self.assertRaises(redisutil.KeyNotFoundError, self.cli.get, 'foo')
        self.assertRaises(redisutil.KeyNotFoundError, self.cli.hget, 'foo', 'bar')

    def test_server_response_error(self):
        cases = (
            201,
            302,
            403,
            500,
        )

        for status in cases:
            self.response['http-status'] = status
            self.assertRaises(redisutil.ServerResponseError, self.cli.get, 'foo')
            self.assertRaises(redisutil.ServerResponseError, self.cli.hget, 'foo', 'bar')
            self.assertRaises(redisutil.ServerResponseError, self.cli.set, 'foo', 'val')
            self.assertRaises(redisutil.ServerResponseError, self.cli.hset, 'foo', 'bar', 'val')

    def test_get(self):
        cases = (
            ('foo', None),
            ('bar', 1),
            ('123', 2),
            ('foobar123', 3)
        )

        for key, retry_cnt in cases:
            res = self.cli.get(key, retry_cnt)
            time.sleep(0.1)

            exp_path = '{ver}/GET/{k}'.format(ver=self.cli.ver, k=key)
            self.assertEqual(exp_path, TestRedisProxyClient.request['req-path'])

            exp_qs = 'n=3&w=2&r=2'
            self.assertIn(exp_qs, TestRedisProxyClient.request['req-qs'])

            exp_res = {
                'foo': 1,
                'bar': 2,
            }
            self.assertDictEqual(exp_res, res)

    def test_hget(self):
        cases = (
            ('hname1', 'hval1'),
            ('hname2', 'hval2'),
            ('hname3', 'hval3'),
            ('hname4', 'hval4'),
        )

        for hname, hkey in cases:
            res = self.cli.hget(hname, hkey)
            time.sleep(0.1)

            exp_path = '{ver}/HGET/{hn}/{hk}'.format(ver=self.cli.ver, hn=hname, hk=hkey)
            self.assertEqual(exp_path, TestRedisProxyClient.request['req-path'])

            exp_qs = 'n=3&w=2&r=2'
            self.assertIn(exp_qs, TestRedisProxyClient.request['req-qs'])

            exp_res = {
                'foo': 1,
                'bar': 2,
            }

            self.assertDictEqual(exp_res, res)

    def test_set(self):
        cases = (
            ('key1', 'val1', None),
            ('key2', 'val2', 1),
            ('key3', 'val3', 2),
            ('key4', 'val4', 3),

            ('key5', 11, 4),
            ('key6', 22, 5),
        )

        for key, val, expire in cases:
            self.cli.set(key, val, expire)
            time.sleep(0.1)

            exp_path = '{ver}/SET/{k}'.format(ver=self.cli.ver, k=key)
            self.assertEqual(exp_path, TestRedisProxyClient.request['req-path'])

            exp_qs = 'n=3&w=2&r=2'
            if expire is not None:
                exp_qs += '&expire={e}'.format(e=expire)

            self.assertIn(exp_qs, TestRedisProxyClient.request['req-qs'])
            self.assertEqual(utfjson.dump(val), TestRedisProxyClient.request['req-body'])

    def test_hset(self):
        cases = (
            ('hname1', 'key1', 'val1', None),
            ('hname2', 'key2', 'val2', 1),
            ('hname3', 'key3', 'val3', 2),
            ('hname4', 'key4', 'val4', 3),

            ('hname5', 'key5', 11, 4),
            ('hname6', 'key6', 22, 5),
        )

        for hname, key, val, expire in cases:
            self.cli.hset(hname, key, val, expire=expire)
            time.sleep(0.1)

            exp_path = '{ver}/HSET/{hn}/{hk}'.format(ver=self.cli.ver, hn=hname, hk=key)
            self.assertEqual(exp_path, TestRedisProxyClient.request['req-path'])

            exp_qs = 'n=3&w=2&r=2'
            if expire is not None:
                exp_qs += '&expire={e}'.format(e=expire)

            self.assertIn(exp_qs, TestRedisProxyClient.request['req-qs'])
            self.assertEqual(utfjson.dump(val), TestRedisProxyClient.request['req-body'])

    def test_retry(self):
        # close http server
        self.tearDown()

        cases = (
            (None, 4),
            (0, 4),
            (1, 8),
            (2, 12),
            (3, 16),
            (4, 20),
        )

        sess = {'run_times': 0}

        def _mock_for_retry(req):
            sess['run_times'] += 1
            return req

        for retry_cnt, exp_cnt in cases:
            sess['run_times'] = 0
            with mock.patch('pykit.redisutil.RedisProxyClient._sign_req', side_effect=_mock_for_retry):
                try:
                    self.cli.get('foo', retry=retry_cnt)
                except:
                    pass

                try:
                    self.cli.hget('foo', 'bar', retry=retry_cnt)
                except:
                    pass

                try:
                    self.cli.set('foo', 'val', retry=retry_cnt)
                except:
                    pass

                try:
                    self.cli.hset('foo', 'bar', 'val', retry=retry_cnt)
                except:
                    pass

            self.assertEqual(exp_cnt, sess['run_times'])


class HttpHandle(BaseHTTPRequestHandler):

    def do_PUT(self):
        length = int(self.headers.getheader('Content-Length'))
        rst = []

        while length > 0:
            buf = self.rfile.read(length)
            rst.append(buf)
            length -= len(buf)

        path_res = urlparse.urlparse(self.path)

        TestRedisProxyClient.request['req-body'] = ''.join(rst)
        TestRedisProxyClient.request['req-path'] = path_res.path
        TestRedisProxyClient.request['req-qs'] = path_res.query

        body = TestRedisProxyClient.response.get('body', '')
        self.send_response(TestRedisProxyClient.response['http-status'])
        self.send_header('Content-Length', len(body))
        self.end_headers()

        if len(body) > 0:
            self.wfile.write(body)

    def do_GET(self):
        response = utfjson.dump({
            'foo': 1,
            'bar': 2,
        })

        path_res = urlparse.urlparse(self.path)

        TestRedisProxyClient.request['req-path'] = path_res.path
        TestRedisProxyClient.request['req-qs'] = path_res.query

        self.send_response(TestRedisProxyClient.response['http-status'])
        self.send_header('Content-Length', len(response))
        self.end_headers()

        self.wfile.write(response)


def child_exit():

    # to suppress error message caused by sys.exit()
    os.close(0)
    os.close(1)
    os.close(2)

    sys.exit(0)
