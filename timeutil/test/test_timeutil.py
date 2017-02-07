#!/usr/bin/env python2.6
# coding: utf-8

import time
import unittest

import timeutil

test_case = {
    'ts': {
        'day_accuracy': 1485216000,
        'hour_accuracy': 1485241200,
        'second_accuracy': 1485244319,
    },

    'format': {
        'default': 'Tue, 24 Jan 2017 07:51:59 UTC',
        'iso': '2017-01-24T07:51:59.000Z',
        'utc': 'Tue, 24 Jan 2017 07:51:59 UTC',
        'archive': '20170124-07',
        'compact': '20170124-075159',
        'daily': '2017-01-24',
        'mysql': '2017-01-24 07:51:59',
        'nginxaccesslog': '24/Jan/2017:07:51:59',
        'nginxerrorlog': '2017/01/24 07:51:59',
    },
}


class TestTimeutil(unittest.TestCase):

    def test_parse(self):

        for fmt_key, tm_str in test_case['format'].items():

            dt = timeutil.parse(tm_str, fmt_key)
            ts = timeutil.utc_datetime_to_ts(dt)

            if fmt_key == 'archive':
                self.assertEqual(test_case['ts']['hour_accuracy'], ts)
            elif fmt_key == 'daily':
                self.assertEqual(test_case['ts']['day_accuracy'], ts)
            else:
                self.assertEqual(test_case['ts']['second_accuracy'], ts)

    def test_format(self):

        dt = timeutil.ts_to_datetime(test_case['ts']['second_accuracy'])

        for fmt_key, tm_str in test_case['format'].items():

            convert_tm_str = timeutil.format(dt, fmt_key)

            self.assertEqual(tm_str, convert_tm_str)

    def test_format_ts(self):

        for fmt_key, tm_str in test_case['format'].items():

            convert_tm_str = \
                timeutil.format_ts(test_case['ts']['second_accuracy'], fmt_key)

            self.assertEqual(tm_str, convert_tm_str)

    def test_ts_and_datetime_conversion(self):

        ts = timeutil.ts()

        dt = timeutil.ts_to_datetime(ts)
        converted_ts = timeutil.utc_datetime_to_ts(dt)

        self.assertEqual(ts, converted_ts)

    def test_timestamp(self):

        cases = [
            (timeutil.ts, 10, 1, 2),
            (timeutil.ms, 13, 0.001, 3),
            (timeutil.us, 16, 0.000001, 30),
        ]

        for case in cases:
            timestamp_func, length, unit_ts, tolerance_ts = case

            ts1 = timestamp_func()

            time.sleep(unit_ts)

            ts2 = timestamp_func()

            self.assertTrue(ts1 < ts2 and ts2 < ts1 + tolerance_ts)

            self.assertEqual(length, len(str(ts2)))

    def test_convert_to_ts(self):

        ts = timeutil.ts()

        ms = ts * 1000
        us = ts * 1000000

        self.assertEqual(ts, timeutil.ms_to_ts(ms))
        self.assertEqual(ts, timeutil.us_to_ts(us))
