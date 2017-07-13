#!/usr/bin/env python2
# coding: utf-8

import os
import subprocess
import time
import unittest
import random
import websocket
from pykit.wsjobd.test.wsjobd_server import PORT
from pykit import utfjson

random.seed(time.time())
this_base = os.path.dirname(__file__)


def subproc(script):

    subproc = subprocess.Popen(['sh'],
                               close_fds=True,
                               env=dict(
                                       PYTHONPATH='/usr/local/s2/current',
                               ),
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)


    out, err = subproc.communicate(script)
    subproc.wait()

    if subproc.returncode != 0:
        print out
        print err

    return (subproc.returncode, out, err)


class TestWsjobd(unittest.TestCase):

    def _clean(self):
        try:
            subproc('python2 {b}/wsjobd_server.py stop'.format(b=this_base))
        except Exception as e:
            print repr(e)

        time.sleep(0.1)

    @classmethod
    def setUpClass(cls):
        subproc('cp pykit/wsjobd/test/test_jobs/test_job_*.py jobs')

    @classmethod
    def tearDownClass(cls):
        subproc('rm -f jobs/test_job_*.py')
        subproc('rm -f jobs/test_job_*.pyc')

    def setUp(self):
        self._clean()

    def tearDown(self):
        self._clean()

    def get_connection(self):
        ws = websocket.WebSocket()
        ws.connect('ws://127.0.0.1:%d' % PORT)
        ws.timeout = 6

        return ws

    def get_random_ident(self):
        return 'random_ident_%d' % random.randint(10000, 99999)

    def test_invalid_jobdesc(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        cases = (
            ('foo', 'not json'),
            (utfjson.dump('foo'), 'not dict'),
            (utfjson.dump({}), 'no func'),
            (utfjson.dump({'func': 'foo'}), 'no ident'),
            (utfjson.dump({'ident': 'bar'}), 'no func'),
        )
        for msg, desc in cases:
            ws = self.get_connection()

            ws.send(msg)

            resp = utfjson.load(ws.recv())
            self.assertEqual(True, 'err' in resp, desc)

            ws.close()

    def test_normal_job(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        job_desc = {
            'func': 'test_job_normal.run',
            'ident': self.get_random_ident(),
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = utfjson.load(ws.recv())
        self.assertEqual('foo', resp['result'], 'test get result')

    def test_report_interval(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        job_desc = {
            'func': 'test_job_loop_10.run',
            'ident': self.get_random_ident(),
            'progress': {
                'interval': 0.5,
            },
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        ws.recv()
        first_report_time = time.time()

        ws.recv()
        second_report_time = time.time()

        actual_interval = second_report_time - first_report_time

        diff = actual_interval - job_desc['progress']['interval']

        # tolerate 0.1 second of difference
        self.assertLess(diff, 0.1)

    def test_progress_key(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        job_desc = {
            'func': 'test_job_progress_key.run',
            'ident': self.get_random_ident(),
            'progress': {
                'key': 'foo',
            },
            'report_system_load': True,
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = ws.recv()
        resp = utfjson.load(resp)
        self.assertEqual('80%', resp)

    def test_check_system_load(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        job_desc = {
            'func': 'test_job_normal.run',
            'ident': self.get_random_ident(),
            'check_load': {
                'mem_low_threshold': 100 * 1024 ** 3,
                'cpu_low_threshold': 0,
            },
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = ws.recv()
        resp = utfjson.load(resp)
        self.assertEqual('SystemOverloadError', resp['err'])

        job_desc = {
            'func': 'test_job_normal.run',
            'ident': self.get_random_ident(),
            'check_load': {
                'cpu_low_threshold': 100.1,
                'mem_low_threshold': 0,
            },
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = ws.recv()
        resp = utfjson.load(resp)
        self.assertEqual('SystemOverloadError', resp['err'])

    def test_max_client_number(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        job_desc = {
            'func': 'test_job_loop_10.run',
            'ident': self.get_random_ident(),
            'check_load': {
                'max_client_number': 1,
                'cpu_low_threshold': 0,
                'mem_low_threshold': 0,
            },
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = ws.recv()
        resp = utfjson.load(resp)
        self.assertEqual(False, 'err' in resp)

        job_desc = {
            'func': 'test_job_loop_10.run',
            'ident': self.get_random_ident(),
            'check_load': {
                'max_client_number': 1,
                'cpu_low_threshold': 0,
                'mem_low_threshold': 0,
            },
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = ws.recv()
        resp = utfjson.load(resp)
        self.assertEqual('SystemOverloadError', resp['err'])

    def test_check_system_load_use_default(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        job_desc = {
            'func': 'test_job_normal.run',
            'ident': self.get_random_ident(),
            'check_load': {
            },
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = ws.recv()
        resp = utfjson.load(resp)
        self.assertEqual(False, 'err' in resp)

    def test_function_not_exists(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        job_desc = {
            'func': 'foo.bar',
            'ident': self.get_random_ident(),
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = utfjson.load(ws.recv())
        self.assertEqual(True, 'err' in resp)

    def test_report_system_load(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        job_desc = {
            'func': 'test_job_normal.run',
            'ident': self.get_random_ident(),
            'report_system_load': True,
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = utfjson.load(ws.recv())
        self.assertEqual(True, 'mem_available' in resp['system_load'])
        self.assertEqual(True, 'cpu_idle_percent' in resp['system_load'])
        self.assertEqual(True, 'client_number' in resp['system_load'])

    def test_same_ident_same_job(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        ident = self.get_random_ident()
        job_desc = {
            'func': 'test_job_echo.run',
            'ident': ident,
            'echo': 'foo',
            'sleep_time': 10,
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = utfjson.load(ws.recv())
        self.assertEqual('foo', resp['result'])

        job_desc = {
            'func': 'test_job_echo.run',
            'ident': ident,
            'echo': 'bar',
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = utfjson.load(ws.recv())
        # not bar, because the ident is same as the first job,
        # if job exists, it will not create a new one
        self.assertEqual('foo', resp['result'])
        self.assertEqual('foo', resp['echo'])

    def test_same_ident_different_job(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        ident = self.get_random_ident()
        job_desc = {
            'func': 'test_job_echo.run',
            'ident': ident,
            'echo': 'foo',
            'sleep_time': 0.1,
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = utfjson.load(ws.recv())
        self.assertEqual('foo', resp['result'])

        time.sleep(0.2)

        job_desc = {
            'func': 'test_job_echo.run',
            'ident': ident,
            'echo': 'bar',
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = utfjson.load(ws.recv())
        # old job with the same ident has exit, it will create a new one
        self.assertEqual('bar', resp['result'])
        self.assertEqual('bar', resp['echo'])

    def test_client_close(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        ident = self.get_random_ident()
        job_desc = {
            'func': 'test_job_echo.run',
            'ident': ident,
            'echo': 'foo',
            'time_sleep': 10,
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))
        ws.close()

        job_desc = {
            'func': 'test_job_echo.run',
            'ident': ident,
            'echo': 'bar',
            'time_sleep': 10,
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = ws.recv()
        resp = utfjson.load(resp)
        self.assertEqual('foo', resp['result'])

    def test_invalid_cpu_sample_interval(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        job_desc = {
            'func': 'test_job_normal.run',
            'ident': self.get_random_ident(),
            'cpu_sample_interval': 'foo',
        }

        ws = self.get_connection()
        ws.send(utfjson.dump(job_desc))

        resp = utfjson.load(ws.recv())
        self.assertEqual('InvalidMessageError', resp['err'])

    def test_invalid_check_load_args(self):
        subproc('python2 {b}/wsjobd_server.py start'.format(b=this_base))
        cases = (
            {'check_load': {'mem_low_threshold': 'foo'}},
            {'check_load': {'cpu_low_threshold': None}},
            {'check_load': {'max_client_number': {}}},
        )

        job_desc = {
            'func': 'test_job_normal.run',
        }

        for case in cases:
            case.update(job_desc)
            case['ident'] = self.get_random_ident()

            ws = self.get_connection()
            ws.send(utfjson.dump(case))

            resp = utfjson.load(ws.recv())
            self.assertEqual('InvalidMessageError', resp['err'])
