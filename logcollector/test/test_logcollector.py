#!/usr/bin/env python2
# coding: utf-8

import os
import re
import time
import unittest

from pykit import logutil
from pykit import threadutil
from pykit import timeutil
from pykit import ututil
from pykit.logcollector import collector

dd = ututil.dd

this_base = os.path.dirname(__file__)

standard_level = {
    'ERROR': 'error',
    'WARNING': 'warning',
    'INFO': 'info',
}


def is_first_line(line):
    return True


def parse(log_str):
    r = re.match('^\[(.+?),(.+?),(.+?),(.+?),(\d+?),(\w+?)]', log_str)

    time_str = r.group(1)

    log_dt = timeutil.parse(time_str, 'mysql')
    log_ts = int(time.mktime(log_dt.timetuple()))

    source_file = r.group(4)
    line_number = int(r.group(5))
    level = standard_level[r.group(6)]

    log_info = {
        'log_ts': log_ts,
        'level': level,
        'source_file': source_file,
        'line_number': line_number,
    }

    return log_info


class TestLogcollector(unittest.TestCase):

    def _clean(self):
        try:
            os.unlink(os.path.join(this_base, 'test_log.out'))
        except Exception as e:
            dd(repr(e))

    def setUp(self):
        self._clean()

    def tearDown(self):
        self._clean()

    def log(self):
        logger = logutil.make_logger(base_dir=this_base,
                                     log_name='test_log')

        cnt = 1
        while True:
            logger.info('info')
            logger.warn('warn')
            logger.error('error')
            time.sleep(0.001)
            cnt += 1
            if cnt > 100:
                break

    def get_level(self, log_str):
        for k in standard_level:
            if k in log_str:
                return k.lower()
        else:
            return 'unknown'

    def test_basic(self):
        log_entries = []

        def send_log(log_entry):
            log_entries.append(log_entry)

        kwargs = {
            'node_id': '123abc',
            'node_ip': '1.2.3.4',
            'send_log': send_log,
            'conf': {
                'my_test_log': {
                    'file_path': os.path.join(this_base, 'test_log.out'),
                    'level': ['error'],
                    'get_level': self.get_level,
                    'is_first_line': is_first_line,
                    'parse': parse,
                },
            },
        }

        threadutil.start_daemon(self.log)
        threadutil.start_daemon(collector.run, kwargs=kwargs)
        time.sleep(8)

        dd(log_entries)
        log_cnt = 0
        for le in log_entries:
            log_cnt += le["count"]
        dd(log_cnt)

        self.assertEqual(100, log_cnt)
        self.assertEqual('error', log_entries[0]['level'])
        self.assertEqual('my_test_log', log_entries[0]['log_name'])
        self.assertEqual('test_log.out', log_entries[0]['log_file'])

    def test_no_merge(self):
        log_entries = []

        def send_log(log_entry):
            print log_entry
            log_entries.append(log_entry)

        kwargs = {
            'node_id': '123abc',
            'node_ip': '1.2.3.4',
            'send_log': send_log,
            'conf': {
                'my_test_log': {
                    'file_path': os.path.join(this_base, 'test_log.out'),
                    'level': ['error'],
                    'get_level': self.get_level,
                    'is_first_line': is_first_line,
                    'parse': parse,
                    'merge': False,
                },
            },
        }

        threadutil.start_daemon(self.log)
        threadutil.start_daemon(collector.run, kwargs=kwargs)
        time.sleep(8)

        self.assertEqual(100, len(log_entries))
        self.assertEqual('error', log_entries[0]['level'])
