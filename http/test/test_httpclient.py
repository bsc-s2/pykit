#!/usr/bin/env python2
# coding: utf-8

import gc
import os
import socket
import ssl
import threading
import time
import unittest
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer

from pykit import http
from pykit import ututil

dd = ututil.dd


HOST = '127.0.0.1'
PORT = 38002
KB = 1024
MB = (1024**2)
HOME_PATH = os.path.dirname(os.path.abspath(__file__))


class TestHttpClient(unittest.TestCase):

    special_cases = {
        'test_recving_server_close':
        (0, 1, 'HTTP/1.1 200 OK\r\nContent-Length: 10\r\n\r\n'),

        'test_server_delay_response':
        (0.5, 1, 'HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\nabcd'),

        'test_raise_chunked_size_error':
        (0, 10, 'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\nfoo\r\n'),

        'test_raise_socket_timeout':
        (3, 1, 'H'),

        'test_raise_line_too_long_error':
        (0, KB, 'a' * 65536),

        'test_request_chunked':
        (),

        'test_readlines':
        (0, 10, 'HTTP/1.1 200 OK\r\nContent-Length: 131086\r\n\r\n' + 'a'*65540 + '\r\nbb\r\n' + 'c'*65540),

        'test_readlines_delimiter':
        (0, 10, 'HTTP/1.1 200 OK\r\nContent-Length: 15\r\n\r\nabcd\rbcde\rcdef\r'),

    }
    request_headers = {}
    request_body = {}

    def test_raise_connnect_error(self):

        h = http.Client(HOST, PORT)
        self.assertRaises(http.NotConnectedError, h.send_body, None)

    def test_raise_line_too_long_error(self):

        h = http.Client(HOST, PORT)
        self.assertRaises(http.LineTooLongError,
                          h.request, '/line_too_long')

    def test_raise_response_headers_error(self):

        cases = (
            '/invalid_content_len',
            '/invalid_header',
        )
        h = http.Client(HOST, PORT)
        for uri in cases:
            self.assertRaises(http.HeadersError, h.request, uri)

    def test_raise_chunked_size_error(self):

        h = http.Client(HOST, PORT)
        h.request('')
        self.assertRaises(http.ChunkedSizeError, h.read_body, 10)

    def test_raise_response_not_ready_error(self):

        h = http.Client(HOST, PORT)
        self.assertRaises(http.ResponseNotReadyError, h.read_response)

    def test_raise_socket_timeout(self):

        h = http.Client(HOST, PORT, 2)
        self.assertRaises(socket.timeout, h.request, '')

    def test_raise_badstatus_line_error(self):

        cases = (
            '/invalid_line',
            '/invalid_protocol',
            '/<100',
            '/>999',
        )

        h = http.Client(HOST, PORT)
        for uri in cases:

            self.assertRaises(http.BadStatusLineError, h.request, uri)

    def test_raise_socket_error(self):

        h = http.Client(HOST, PORT)
        h.request('/socket_error')
        self.assertRaises(socket.error, h.read_body, 10)

    def test_get_http_request(self):

        cases = (
            ('/get_1b', 1, 'a', (), False),
            ('/get_1b', 10, 'a', (), False),
            ('/get_1b', None, 'a', (), False),
            ('/get_10k', KB, 'bc' * 5 * KB, (), False),
            ('/get_10k', 20 * KB, 'bc' * 5 * KB, (), False),
            ('/get_10k', None, 'bc' * 5 * KB, (), False),
            ('/get_30m', 10 * MB, 'cde' * 10 * MB, (), False),
            ('/get_30m', 50 * MB, 'cde' * 10 * MB, (), False),
            ('/get_30m', None, 'cde' * 10 * MB, (), False),

            ('/get_10b_chunked', 1, 'f' * 10, (), True),
            ('/get_10b_chunked', 10, 'f' * 10, (), True),
            ('/get_10b_chunked', None, 'f' * 10, (), True),
            ('/get_10k_chunked', KB, 'gh' * 5 * KB, (), True),
            ('/get_10k_chunked', 20 * KB, 'gh' * 5 * KB, (), True),
            ('/get_10k_chunked', None, 'gh' * 5 * KB, (), True),
            ('/get_30m_chunked', 10 * MB, 'ijk' * 10 * MB, (), True),
            ('/get_30m_chunked', 50 * MB, 'ijk' * 10 * MB, (), True),
            ('/get_30m_chunked', None, 'ijk' * 10 * MB, (), True),

            ('/get_10b_range', 1, 'l' * 10, (2, 8), False),
            ('/get_10b_range', 10, 'l' * 10, (2, 8), False),
            ('/get_10b_range', None, 'l' * 10, (2, 8), False),
            ('/get_10k_range', KB, 'mn' * 5 * KB, (KB, 8 * KB), False),
            ('/get_10k_range', 20 * KB, 'mn' * 5 * KB, (KB, 8 * KB), False),
            ('/get_10k_range', None, 'mn' * 5 * KB, (KB, 8 * KB), False),
            ('/get_30m_range', 10 * MB, 'opq' * 10 * MB, (2 * MB, 25 * MB), False),
            ('/get_30m_range', 50 * MB, 'opq' * 10 * MB, (2 * MB, 25 * MB), False),
            ('/get_30m_range', None, 'opq' * 10 * MB, (2 * MB, 25 * MB), False),
        )
        h = http.Client(HOST, PORT)
        for uri, each_read_size, expected_res, content_range, chunked in cases:
            h.request(uri)

            bufs = ''
            if each_read_size is None:
                bufs = h.read_body(None)
                self.assertEqual(h.has_read, len(bufs))
            else:
                while True:
                    b = h.read_body(each_read_size)
                    if len(b) <= 0:
                        break
                    bufs += b
                    self.assertEqual(h.has_read, len(bufs))

            start, end = 0, len(expected_res)
            if len(content_range) >= 2:
                start, end = content_range[0], content_range[1] + 1

            self.assertEqual(expected_res[start:end], bufs)
            self.assertEqual(None if chunked else len(bufs), h.content_length)
            self.assertEqual(chunked, h.chunked)

    def test_status(self):

        cases = (
            ('/get_200', 200),
            ('/get_304', 304),
            ('/get_404', 404),
            ('/get_500', 500),
        )

        h = http.Client(HOST, PORT)
        for uri, expected_status in cases:
            h.request(uri)

            self.assertEqual(expected_status, h.status)

    def test_request_chunked(self):

        h = http.Client(HOST, PORT)
        h.send_request('', 'PUT', {'Transfer-Encoding': 'chunked'})

        cases = (
            ('aaaaaaaaa', 100),
            ('bbbbbbbbbbbbbb', 100),
            ('0000000000000', 100),
            ('200_status', 200)
                )

        for body, status in cases:
            h.send_body(body)
            self.assertEqual(h.read_status(False), status)

    def test_request_headers(self):

        cases = (
            ('/header_1', {'host': 'example.com'}),
            ('/header_2', {'host': 'example.com', 'b': 'bar'}),
            ('/header_3', {'host': 'example.com', 'b': 'bar', 'f': 'foo'}),
        )

        h = http.Client(HOST, PORT)
        for uri, headers in cases:
            h.request(uri, headers=headers)
            time.sleep(0.1)

            self.assertEqual(headers, self.request_headers)

    def test_response_headers(self):

        cases = (
            ('/header_res1', {'f': 'foo'}),
            ('/header_res2', {'f': 'foo', 'b': 'bar'}),
            ('/header_res3', {'f': 'foo', 'b': 'bar', 't': 'too'}),
        )

        h = http.Client(HOST, PORT)
        for uri, expected_headers in cases:
            h.request(uri)

            self.assertEqual(expected_headers, h.headers)

    def test_send_body(self):

        cases = (
            ('/put_1b', 'a', {'Content-Length': 1}),
            ('/put_10k', 'bc' * 5 * KB, {'Content-Length': 10 * KB}),
            ('/put_30m', 'cde' * 10 * MB, {'Content-Length': 30 * MB}),
        )

        h = http.Client(HOST, PORT)
        for uri, body, headers in cases:
            h.send_request(uri, method='PUT', headers=headers)
            h.send_body(body)
            h.read_response()
            time.sleep(0.1)

            self.assertEqual(body, self.request_body)

    def test_readlines(self):

        h = http.Client(HOST, PORT)
        h.request('')

        expected_body = ('a' * 65540 + '\r\n', 'bb\r\n', 'c' * 65540)
        for idx, line in enumerate(h.readlines()):
            self.assertEqual(expected_body[idx], line)

    def test_readlines_delimiter(self):

        h = http.Client(HOST, PORT)
        h.request('')

        expected_body = ('abcd\r', 'bcde\r', 'cdef\r')
        for idx, line in enumerate(h.readlines('\r')):
            self.assertEqual(expected_body[idx], line)

    def test_recving_server_close(self):

        h = http.Client(HOST, PORT, 3)
        succ = False

        try:
            h.request('')
            h.read_body(1024)
        except socket.error as e:
            dd(repr(e) + ' while recv server close')
            succ = True
        except Exception as e:
            dd(repr(e) + ' unexpected exception')

        self.assertTrue(succ)

    def test_server_delay_response(self):

        case = ({'content-length': '4'}, 'abcd')
        expected_headers, expected_body = case

        h = http.Client(HOST, PORT, 1)
        h.request('')
        body = h.read_body(1024)

        self.assertEqual(expected_headers, h.headers)
        self.assertEqual(expected_body, body)

    def test_client_delay_send_data(self):

        case = ('/client_delay', {'Content-Length': 10}, 'abcde' * 2)
        uri, headers, body = case

        h = http.Client(HOST, PORT, 3)
        h.send_request(uri, method='PUT', headers=headers)

        while len(body) > 0:
            h.send_body(body[:1])
            time.sleep(1)
            body = body[1:]

        self.assertEqual(case[2], self.request_body)

    def test_garbage_collector(self):

        h = http.Client(HOST, PORT)
        h.request('/get_30m')
        h.read_body(None)
        del h

        gc.collect()
        self.assertListEqual([], gc.garbage)

    def test_trace(self):

        class FakeErrorDuringHTTP(Exception):
            pass

        h = http.Client(HOST, PORT)
        h.request('/get_10k')
        h.read_body(1)
        h.read_body(None)

        # emulate error
        try:
            with h.stopwatch.timer('exception'):
                raise FakeErrorDuringHTTP(3)
        except Exception:
            pass

        trace = h.get_trace()
        dd('trace:', trace)

        ks = (
            'conn',
            'send_header',
            'recv_status',
            'recv_header',
            'recv_body',
        )

        for i, k in enumerate(ks):
            self.assertEqual(k, trace[i]['name'])
            self.assertEqual(type(0.1), type(trace[i]['time']))

        names = [x['name'] for x in trace]
        self.assertEqual(['conn',
                          'send_header',
                          'recv_status',
                          'recv_header',
                          'recv_body',
                          'recv_body',
                          'exception',
                          'pykit.http.Client'],
                         names)

        dd('trace str:', h.get_trace_str())

    def test_trace_min_tracing_milliseconds(self):

        h = http.Client(HOST, PORT, stopwatch_kwargs={
                        'min_tracing_milliseconds': 1000})
        h.request('/get_10k')
        h.read_body(None)

        # only steps cost time>1000 are traced. thus nothing should be traced
        trace_str = h.get_trace_str()
        dd('trace:', trace_str)

        self.assertEqual('', trace_str)

        self.assertEqual([], h.get_trace())

    def test_https(self):
        cases = (
            ('/get_1b', 'a'),
            ('/get_10k', 'bc' * 5 * KB),
            ('/get_30m', 'cde' * 10 * MB),
        )

        context = ssl._create_unverified_context()
        cli = http.Client(HOST, PORT, https_context=context)
        for uri, expected_res in cases:
            cli.request(uri)
            body = cli.read_body(None)

            self.assertEqual(200, cli.status)
            self.assertEqual(expected_res, body)

    def __init__(self, *args, **kwargs):

        super(TestHttpClient, self).__init__(*args, **kwargs)
        self.server_thread = None
        self.http_server = None

    def setUp(self):

        self.server_thread = threading.Thread(target=self._start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(0.1)

    def tearDown(self):

        if self.http_server is not None:
            self.http_server.shutdown()
            self.http_server.server_close()

        self.server_thread.join()

    def _start_server(self):

        if self._testMethodName in self.special_cases:
            self._special_case_handle()
        else:
            addr = (HOST, PORT)
            self.http_server = HTTPServer(addr, Handle)
            if 'https' in self._testMethodName:
                cert_file = os.path.join(HOME_PATH, 'test_https.pem')
                self.http_server.socket = ssl.wrap_socket(self.http_server.socket,
                                                          certfile=cert_file,
                                                          server_side=True)
            self.http_server.serve_forever()

    def _special_case_handle(self):

        addr = (HOST, PORT)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr)
        sock.listen(10)


        if self._testMethodName == 'test_request_chunked':

            conn, _ = sock.accept()
            for i in range(3):
                data = conn.recv(1024)
                dd('recv data:' + data)

                res = 'HTTP/1.1 100 CONTINUE\r\n\r\n'
                conn.sendall(res)

            data = conn.recv(1024)
            dd('recv data:' + data)
            res = 'HTTP/1.1 200 OK\r\n\r\n'
            conn.sendall(res)

        else:
            conn, _ = sock.accept()
            data = conn.recv(1024)
            dd('recv data:' + data)
            res = self.special_cases.get(self._testMethodName)
            if res is None:
                return

            sleep_time, each_send_size, content = res
            try:
                while len(content) > 0:
                    conn.sendall(content[:each_send_size])
                    content = content[each_send_size:]
                    time.sleep(sleep_time)
            except socket.error as e:
                dd(repr(e) + ' while response')

        time.sleep(1)
        conn.close()
        sock.close()


class Handle(BaseHTTPRequestHandler):

    all_responses = {
        '/invalid_content_len': (200, {'content-length': 'abc'}, (0, '')),
        '/invalid_header': (200, {}, (0, '')),

        '/get_1b': (200, {'content-length': 1}, (1, 'a')),
        '/get_10k': (200, {'content-length': 10 * KB}, (10240, 'bc' * 5 * KB)),
        '/get_30m': (200, {'content-length': 30 * MB}, (10 * MB, 'cde' * 10 * MB)),

        '/get_10b_chunked': (200, {'Transfer-Encoding': 'chunked'}, (5, 'f' * 10)),
        '/get_10k_chunked': (200, {'Transfer-Encoding': 'chunked'}, (KB, 'gh' * 5 * KB)),
        '/get_30m_chunked': (200, {'Transfer-Encoding': 'chunked'}, (10 * MB, 'ijk' * 10 * MB)),

        '/get_10b_range': (206,
                           {'Content-Range': 'bytes %d-%d/%d' % (2, 8, 10),
                            'Content-Length': 7},
                           (5, 'l' * 10)),
        '/get_10k_range': (206,
                           {'Content-Range': 'bytes %d-%d/%d' % (KB, 8 * KB, 10 * KB),
                            'Content-Length': 7 * KB + 1},
                           (KB, 'mn' * 5 * KB)),
        '/get_30m_range': (206,
                           {'Content-Range': 'bytes %d-%d/%d' % (2 * MB, 25 * MB, 30 * MB),
                            'Content-Length': 23 * MB + 1},
                           (10 * MB, 'opq' * 10 * MB)),

        '/get_200': (200, {}, (0, '')),
        '/get_304': (304, {}, (0, '')),
        '/get_404': (404, {}, (0, '')),
        '/get_500': (500, {}, (0, '')),

        '/header_1': (200, {}, (0, '')),
        '/header_2': (200, {}, (0, '')),
        '/header_3': (200, {}, (0, '')),

        '/header_res1': (200, {'f': 'foo'}, (0, '')),
        '/header_res2': (200, {'f': 'foo', 'b': 'bar'}, (0, '')),
        '/header_res3': (200, {'f': 'foo', 'b': 'bar', 't': 'too'}, (0, '')),

        '/invalid_line': (200, {}, (0, '')),
        '/invalid_protocol': (200, {}, (0, '')),
        '/<100': (10, {}, (0, '')),
        '/>999': (1000, {}, (0, '')),

        '/socket_error': (200, {'Content-Length': 10}, (0, '')),
    }

    def send_response(self, code, message=None):

        self.log_request(code)
        if message is None:
            if code in self.responses:
                message = self.responses[code][0]
            else:
                message = ''
        if self.request_version != 'HTTP/0.9':
            if self.path == '/invalid_protocol':
                protocol = 'foo'
            elif self.path == '/invalid_line':
                self.wfile.write(self.protocol_version + '\r\n')
                return
            else:
                protocol = self.protocol_version
            self.wfile.write("%s %d %s\r\n" %
                             (protocol, code, message))
            if self.path == '/invalid_header':
                self.wfile.write('foo\r\n')

    def do_PUT(self):

        try:
            length = int(self.headers.getheader('Content-Length'))
        except (TypeError, ValueError) as e:
            dd(repr(e))
            return

        read_bytes = 0
        bufs = ''

        try:
            while read_bytes < length:
                bufs += self.rfile.read(length - read_bytes)
                read_bytes = len(bufs)

            TestHttpClient.request_body = bufs
            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()
        except Exception as e:
            dd(repr(e) + ' while parse put request')

    def do_GET(self):

        TestHttpClient.request_headers = self.headers.dict

        res = self.all_responses.get(self.path)
        if res is None:
            dd('path error:' + self.path)
            return

        status, headers, body = res

        try:
            self.send_response(status)

            for k, v in headers.items():
                self.send_header(k, v)
            self.end_headers()

            self._send_body(headers, body)
        except Exception as e:
            dd(repr(e) + ' while parse get request')

    def _send_body(self, headers, body):

        each_send_size, data = self._get_body(headers, body)
        ext = ';extname'
        while len(data) > 0:
            send_buf = data[:each_send_size]
            if 'Transfer-Encoding' in headers:
                if len(ext) > 0:
                    ext = ''
                else:
                    ext = ';extname'
                send_buf = '%x%s\r\n%s\r\n' % (len(send_buf), ext, send_buf)

            self.wfile.write(send_buf)
            data = data[each_send_size:]

        if 'Transfer-Encoding' in headers:
            self.wfile.write('0\r\n\r\n')

    def _get_body(self, headers, body):

        each_send_size, data = body
        start = 0
        end = len(data)
        if 'Content-Range' in headers:
            val = headers['Content-Range'][6:]
            val = val[:val.find('/')]
            start, end = val.split('-', 1)

        return each_send_size, data[int(start):int(end) + 1]
