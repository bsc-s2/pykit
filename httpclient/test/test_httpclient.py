#!/usr/bin/env python2
# coding: utf-8

import socket
import threading
import time
import unittest
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer

from pykit import httpclient
from pykit import ututil

dd = ututil.dd


HOST = '127.0.0.1'
PORT = 38002
KB = 1024
MB = (1024**2)


class TestHttpClient(unittest.TestCase):

    request_headers = {}
    request_body = {}

    def test_raise_connnect_error(self):

        h = httpclient.HttpClient(HOST, PORT)
        self.assertRaises(httpclient.NotConnectedError, h.send_body, None)

    def test_raise_line_too_long_error(self):

        h = httpclient.HttpClient(HOST, PORT)
        self.assertRaises(httpclient.LineTooLongError,
                          h.request, '/line_too_long')

    def test_raise_response_headers_error(self):

        cases = (
            '/invalid_content_len',
            '/invalid_header',
        )
        h = httpclient.HttpClient(HOST, PORT)
        for uri in cases:
            self.assertRaises(httpclient.HeadersError, h.request, uri)

    def test_raise_chunked_size_error(self):

        h = httpclient.HttpClient(HOST, PORT)
        h.request('/chunked_size_error')
        self.assertRaises(httpclient.ChunkedSizeError, h.read_body, 10)

    def test_raise_response_not_ready_error(self):

        h = httpclient.HttpClient(HOST, PORT)
        self.assertRaises(httpclient.ResponseNotReadyError, h.read_headers)

    def test_raise_socket_timeout(self):

        h = httpclient.HttpClient(HOST, PORT, 2)
        h.request('/get_10k_sleep3')
        self.assertRaises(socket.timeout, h.read_body, 10 * KB)
        time.sleep(2)

    def test_raise_badstatus_line_error(self):

        cases = (
            '/invalid_line',
            '/invalid_protocol',
            '/<100',
            '/>999',
        )

        h = httpclient.HttpClient(HOST, PORT)
        for uri in cases:

            self.assertRaises(httpclient.BadStatusLineError, h.request, uri)

    def test_raise_socket_error(self):

        h = httpclient.HttpClient(HOST, PORT)
        h.request('/socket_error')
        self.assertRaises(socket.error, h.read_body, 10)

    def test_get_http_request(self):

        cases = (
            ('/get_1b', 1, 'a', (), False),
            ('/get_1b', 10, 'a', (), False),
            ('/get_10k', KB, 'bc' * 5 * KB, (), False),
            ('/get_10k', 20 * KB, 'bc' * 5 * KB, (), False),
            ('/get_30m', 10 * MB, 'cde' * 10 * MB, (), False),
            ('/get_30m', 50 * MB, 'cde' * 10 * MB, (), False),

            ('/get_10b_chunked', 1, 'f' * 10, (), True),
            ('/get_10b_chunked', 10, 'f' * 10, (), True),
            ('/get_10k_chunked', KB, 'gh' * 5 * KB, (), True),
            ('/get_10k_chunked', 20 * KB, 'gh' * 5 * KB, (), True),
            ('/get_30m_chunked', 10 * MB, 'ijk' * 10 * MB, (), True),
            ('/get_30m_chunked', 50 * MB, 'ijk' * 10 * MB, (), True),

            ('/get_10b_range', 1, 'l' * 10, (2, 8), False),
            ('/get_10b_range', 10, 'l' * 10, (2, 8), False),
            ('/get_10k_range', KB, 'mn' * 5 * KB, (KB, 8 * KB), False),
            ('/get_10k_range', 20 * KB, 'mn' * 5 * KB, (KB, 8 * KB), False),
            ('/get_30m_range', 10 * MB, 'opq' * 10 * MB, (2 * MB, 25 * MB), False),
            ('/get_30m_range', 50 * MB, 'opq' * 10 * MB, (2 * MB, 25 * MB), False),
        )
        h = httpclient.HttpClient(HOST, PORT)
        for uri, each_read_size, expected_res, content_range, chunked in cases:
            h.request(uri)

            bufs = ''
            while True:
                b = h.read_body(each_read_size)
                if len(b) <= 0:
                    break
                bufs += b
                self.assertEqual(h.has_read, len(bufs))

            start, end = 0, len(expected_res)
            if len(content_range) >= 2:
                start, end = content_range[0], content_range[1] + 1

            self.assertEqual(bufs, expected_res[start:end])
            self.assertEqual(h.content_length, None if chunked else len(bufs))
            self.assertEqual(h.chunked, chunked)

    def test_status(self):

        cases = (
            ('/get_200', 200),
            ('/get_304', 304),
            ('/get_404', 404),
            ('/get_500', 500),
        )

        h = httpclient.HttpClient(HOST, PORT)
        for uri, expected_status in cases:
            h.request(uri)

            self.assertEqual(h.status, expected_status)

    def test_request_headers(self):

        cases = (
            ('/header_1', {'host': 'example.com'}),
            ('/header_2', {'host': 'example.com', 'b': 'bar'}),
            ('/header_3', {'host': 'example.com', 'b': 'bar', 'f': 'foo'}),
        )

        h = httpclient.HttpClient(HOST, PORT)
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

        h = httpclient.HttpClient(HOST, PORT)
        for uri, expected_headers in cases:
            h.request(uri)

            self.assertEqual(expected_headers, h.headers)

    def test_server_delay_response(self):

        cases = (
            ('/get_1b_sleep1', 1, 'a', ()),
            ('/get_1b_sleep2', 1, 'a', ()),
            ('/get_10k_sleep1', KB, 'bc' * 5 * KB, ()),
            ('/get_10k_sleep2', KB, 'bc' * 5 * KB, ()),
            ('/get_30m_sleep1', 10 * MB, 'cde' * 10 * MB, ()),
            ('/get_30m_sleep2', 10 * MB, 'cde' * 10 * MB, ()),

            ('/get_10b_chunked_sleep1', 1, 'f' * 10, ()),
            ('/get_10b_chunked_sleep2', 1, 'f' * 10, ()),
            ('/get_10k_chunked_sleep1', KB, 'gh' * 5 * KB, ()),
            ('/get_10k_chunked_sleep2', KB, 'gh' * 5 * KB, ()),
            ('/get_30m_chunked_sleep1', 10 * MB, 'ijk' * 10 * MB, ()),
            ('/get_30m_chunked_sleep2', 10 * MB, 'ijk' * 10 * MB, ()),

            ('/get_10b_range_sleep1', 1, 'l' * 10, (2, 8)),
            ('/get_10b_range_sleep2', 1, 'l' * 10, (2, 8)),
            ('/get_10k_range_sleep1', KB, 'mn' * 5 * KB, (KB, 8 * KB)),
            ('/get_10k_range_sleep2', KB, 'mn' * 5 * KB, (KB, 8 * KB)),
            ('/get_30m_range_sleep1', 10 * MB, 'opq' * 10 * MB, (2 * MB, 25 * MB)),
            ('/get_30m_range_sleep2', 10 * MB, 'opq' * 10 * MB, (2 * MB, 25 * MB)),
        )

        h = httpclient.HttpClient(HOST, PORT, 3)
        for uri, each_read_size, expected_res, content_range in cases:
            h.request(uri)

            bufs = ''
            while True:
                b = h.read_body(each_read_size)
                if len(b) <= 0:
                    break
                bufs += b

            start, end = 0, len(expected_res)
            if len(content_range) >= 2:
                start, end = content_range[0], content_range[1] + 1

            self.assertEqual(bufs, expected_res[start:end])

    def test_send_body(self):

        cases = (
            ('/put_1b', 'a', {'Content-Length': 1}),
            ('/put_10k', 'bc' * 5 * KB, {'Content-Length': 10 * KB}),
            ('/put_30m', 'cde' * 10 * MB, {'Content-Length': 30 * MB}),
        )

        h = httpclient.HttpClient(HOST, PORT)
        for uri, body, headers in cases:
            h.send_request(uri, method='PUT', headers=headers)
            h.send_body(body)
            h.read_headers()
            time.sleep(0.1)

            self.assertEqual(self.request_body, body)

    def __init__(self, *args, **kwargs):

        super(TestHttpClient, self).__init__(*args, **kwargs)
        self.server_thread = None
        self.http_server = None

    def setUp(self):
        self.server_thread = threading.Thread(target=self._start_server)
        self.server_thread.start()
        time.sleep(0.1)

    def tearDown(self):
        self.http_server.shutdown()
        self.http_server.server_close()
        self.server_thread.join()

    def _start_server(self):

        addr = (HOST, PORT)
        self.http_server = HTTPServer(addr, Handle)
        self.http_server.serve_forever()


class Handle(BaseHTTPRequestHandler):

    all_responses = {
        '/line_too_long': (200, {'line': 'a' * 65540}, (0, '')),
        '/invalid_content_len': (200, {'content-length': 'abc'}, (0, '')),
        '/invalid_header': (200, {}, (0, '')),

        '/get_1b': (200, {'content-length': 1}, (1, 'a')),
        '/get_10k': (200, {'content-length': 10 * KB}, (10240, 'bc' * 5 * KB)),
        '/get_30m': (200, {'content-length': 30 * MB}, (10 * MB, 'cde' * 10 * MB)),

        '/get_10b_chunked': (200, {'Transfer-Encoding': 'chunked'}, (5, 'f' * 10)),
        '/get_10k_chunked': (200, {'Transfer-Encoding': 'chunked'}, (KB, 'gh' * 5 * KB)),
        '/get_30m_chunked': (200, {'Transfer-Encoding': 'chunked'}, (10 * MB, 'ijk' * 10 * MB)),

        '/chunked_size_error': (200, {'Transfer-Encoding': 'chunked'}, (0, '')),

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
        while read_bytes < length:
            bufs += self.rfile.read(length - read_bytes)
            read_bytes = len(bufs)

        TestHttpClient.request_body = bufs
        self.send_response(200)
        self.send_header('Content-Length', 0)
        self.end_headers()

    def do_GET(self):

        TestHttpClient.request_headers = self.headers.dict
        uri = self.path
        sleep_time = 0
        if '_sleep' in uri:
            sleep_time = int(uri[uri.find('_sleep'):][6:])
            uri = uri[:uri.find('_sleep')]

        res = self.all_responses.get(uri)
        if res is None:
            dd('path error:' + self.path)
            return

        status, headers, body = res

        self.send_response(status)

        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()

        self._send_body(headers, body, sleep_time)

    def _send_body(self, headers, body, sleep_time):

        if self.path == '/chunked_size_error':
            self.wfile.write('zzz\r\n')
            return

        each_send_size, data = self._get_body(headers, body)
        length = len(data)
        start = 0
        ext = ';extname'
        while length > 0:
            time.sleep(sleep_time)
            send_buf = data[start:start + each_send_size]
            if 'Transfer-Encoding' in headers:
                send_buf = '%x%s\r\n%s\r\n' % (len(send_buf), ext, send_buf)
            self.wfile.write(send_buf)
            start += each_send_size
            length -= each_send_size
            if len(ext) > 0:
                ext = ''
            else:
                ext = ';extname'

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
