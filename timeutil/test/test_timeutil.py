#!/usr/bin/env python2.6
# coding: utf-8

import datetime
import time
import unittest

import pytz

from pykit import timeutil
from pykit import ututil

dd = ututil.dd

test_case = {
    'ts': {
        'day_accuracy': 1485216000,
        'hour_accuracy': 1485241200,
        'second_accuracy': 1485244319,
    },

    'format':             {
        'default':        'Tue, 24 Jan 2017 07:51:59 UTC',
        'iso':            '2017-01-24T07:51:59.000Z',
        'utc':            'Tue, 24 Jan 2017 07:51:59 UTC',
        'archive':        '20170124-07',
        'compact':        '20170124-075159',
        'daily':          '2017-01-24',
        'daily_compact':  '20170124',
        'mysql':          '2017-01-24 07:51:59',
        'nginxaccesslog': '24/Jan/2017:07:51:59',
        'nginxerrorlog':  '2017/01/24 07:51:59',
    },
}


class TestTimeutil(unittest.TestCase):

    def test_direct_format(self):

        for fmt_key, tm_str in test_case['format'].items():

            # parse
            dt_key = timeutil.parse(tm_str, fmt_key)
            dt_direct = timeutil.parse(tm_str, timeutil.formats[fmt_key])

            self.assertTrue(dt_key == dt_direct)

            # format
            self.assertEqual(tm_str, timeutil.format(dt_key, fmt_key))
            self.assertEqual(tm_str,
                             timeutil.format(dt_key,
                                             timeutil.formats[fmt_key]))

            # format_ts
            now = int(time.time())
            self.assertEqual(timeutil.format_ts(now, fmt_key),
                             timeutil.format_ts(now, timeutil.formats[fmt_key]))

    def test_parse(self):

        for fmt_key, tm_str in test_case['format'].items():

            dt = timeutil.parse(tm_str, fmt_key)
            ts = timeutil.utc_datetime_to_ts(dt)

            if fmt_key == 'archive':
                self.assertEqual(test_case['ts']['hour_accuracy'], ts)
            elif fmt_key.startswith('daily'):
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
            (timeutil.us, 16, 0.000001, 300),
            (timeutil.ns, 19, 0.000000001, 30000),
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
        ns = ts * 1000000000

        self.assertEqual(ts, timeutil.ms_to_ts(ms))
        self.assertEqual(ts, timeutil.us_to_ts(us))
        self.assertEqual(ts, timeutil.ns_to_ts(ns))

    def test_to_ts(self):

        ts = timeutil.ts()

        cases = (
            ts,
            ts + 0.1,
            ts * 1000,
            ts * 1000 + 1,
            ts * 1000 + 0.1,

            ts * 1000 * 1000,
            ts * 1000 * 1000 + 1,
            ts * 1000 * 1000 + 0.1,

            ts * 1000 * 1000 * 1000,
            ts * 1000 * 1000 * 1000 + 1,
            ts * 1000 * 1000 * 1000 + 0.1,
        )

        for inp in cases:
            dd(inp, ts)

            self.assertEqual(ts, timeutil.to_sec(inp),
                             'convert {inp} to second'.format(inp=repr(inp)))

            self.assertEqual(ts, timeutil.to_sec(str(inp)),
                             'convert {inp} to second'.format(inp=repr(inp)))

    def test_to_ts_invalid_input(self):

        cases = (
            'a',
            '1',
            '1.1',
            -123456789,
            {},
            [],
            (),
            True,
            datetime.datetime.now(),
        )

        for inp in cases:

            with self.assertRaises(ValueError):
                timeutil.to_sec(inp)

    def test_is_timestamp(self):
        cases = (
            (False,                None, False,),
            (0,                    None, False,),
            ('0',                  None, False,),
            (u'0',                 None, False,),
            ((),                   None, False,),
            ([],                   None, False,),
            ({},                   None, False,),
            (type,                 None, False,),
            (149361634,            None, False,),
            (14936163419,          None, False,),
            (149361634100,         None, False,),
            (14936163410009,       None, False,),
            (149361634100011,      None, False,),
            (14936163410001119,    None, False,),
            (149361634100011122,   None, False,),
            (14936163410001112229, None, False,),
            (1493616341,           None, True,),
            (1493616341000,        None, True,),
            (1493616341000111,     None, True,),
            (1493616341000111222,  None, True,),
            (1493616341,           's',  True,),
            (1493616341,           'ms', False,),
            (1493616341,           'us', False,),
            (1493616341,           'ns', False,),
            (1493616341000,        's',  False,),
            (1493616341000,        'ms', True,),
            (1493616341000,        'us', False,),
            (1493616341000,        'ns', False,),
            (1493616341000111,     's',  False,),
            (1493616341000111,     'ms', False,),
            (1493616341000111,     'us', True,),
            (1493616341000111,     'ns', False,),
            (1493616341000111222,  's',  False,),
            (1493616341000111222,  'ms', False,),
            (1493616341000111222,  'us', False,),
            (1493616341000111222,  'ns', True,),
        )

        for s, unit, expected in cases:

            dd(s, unit, expected)

            rst = timeutil.is_timestamp(s, unit=unit)
            dd('rst: ', rst)

            self.assertEqual(expected, rst)

            # test input as string
            rst = timeutil.is_timestamp(str(s), unit=unit)
            dd('rst(str): ', rst)

            self.assertEqual(expected, rst)

    def test_datetime_to_ts(self):
        ts = time.time()

        dt = datetime.datetime.fromtimestamp(ts)
        r = timeutil.datetime_to_ts(dt)
        self.assertEqual(ts, r)

        test_timezones = (
            'US/Pacific',
            'Europe/Warsaw',
            'Asia/Shanghai',
        )

        for timezone_name in test_timezones:
            dt = datetime.datetime.fromtimestamp(
                ts, tz=pytz.timezone(timezone_name))

            r = timeutil.datetime_to_ts(dt)
            self.assertEqual(ts, r)

    def test_parse_with_timezone(self):
        cases = (
            ('2018-04-03 17:45:01', 'Asia/Shanghai', 1522748701),
            ('2018-04-03 17:45:01', 'UTC', 1522748701 + 3600 * 8),
        )

        for time_str, timezone, exp_ts in cases:
            dt = timeutil.parse(time_str, 'mysql', timezone=timezone)
            ts = timeutil.datetime_to_ts(dt)

            self.assertEqual(exp_ts, ts)
