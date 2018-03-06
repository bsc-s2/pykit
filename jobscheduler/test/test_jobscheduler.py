#!/usr/bin/env python2
# coding: utf-8

import time
import unittest

from pykit import jobscheduler
from pykit import timeutil


class TestJobScheduler(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_next_fire_time(self):
        cases = (
            (
                '2018-03-06 15:08:11',
                {
                    'every': [1, 'hour'],
                    'at': {'minute': 33, 'second': 44},
                },
                '2018-03-06 16:33:44+08:00'
            ),
            (
                '2018-03-06 15:08:11',
                {
                    'every': [1, 'hour'],
                },
                '2018-03-06 16:08:11+08:00',
            ),
            (
                '2018-03-06 15:08:11',
                {
                    'every': [1, 'hour'],
                    'at': {'minute': 0, 'second': 0},
                },
                '2018-03-06 16:00:00+08:00'
            ),
            (
                '2018-03-06 15:00:00',
                {
                    'every': [1, 'hour'],
                    'at': {'minute': 0, 'second': 0},
                },
                '2018-03-06 16:00:00+08:00'
            ),
            (
                '2018-03-06 15:10:02',
                {
                    'every': [2, 'day'],
                    'at': {'minute': 0, 'second': 0},
                },
                '2018-03-08 15:00:00+08:00'
            ),
            (
                '2018-03-06 15:59:59',
                {
                    'every': [1, 'hour'],
                    'at': {'minute': 0, 'second': 0},
                },
                '2018-03-06 16:00:00+08:00'
            ),
            (
                '2018-03-06 15:59:59',
                {
                    'every': [1, 'minute'],
                    'at': {'second': 0},
                },
                '2018-03-06 16:00:00+08:00'
            ),
            (
                '2018-03-06 16:00:00',
                {
                    'every': [1, 'minute'],
                    'at': {'second': 0},
                },
                '2018-03-06 16:01:00+08:00'
            ),
            (
                '2018-03-06 16:00:00',
                {
                    'every': [50, 'second'],
                },
                '2018-03-06 16:00:50+08:00'
            ),
            (
                '2018-03-06 16:00:00',
                {
                    'every': [3, 'month'],
                    'at': {'day': 30, 'hour': 13, 'minute': 23, 'second': 33},
                },
                '2018-06-30 13:23:33+08:00'
            ),
            (
                '2018-06-30 14:23:55',
                {
                    'every': [3, 'month'],
                    'at': {'day': 30, 'hour': 13, 'minute': 23, 'second': 33},
                },
                # not 2018-09-30, because we assume every month is 31 days,
                # so add 3 * 31 days to 2018-06-30 is not 2018-09-30.
                '2018-10-30 13:23:33+08:00'
            ),
            (
                '2018-06-30 13:23:33',
                {
                    'every': [3, 'week'],
                    'at': {'hour': 13, 'minute': 23, 'second': 33},
                },
                '2018-07-21 13:23:33+08:00'
            ),
            (
                '2018-03-06 15:10:02',
                {
                    'every': [1, 'day'],
                    'at': {'hour': 12, 'minute': 0, 'second': 0},
                    'timezone': 'utc',
                },
                '2018-03-07 20:00:00+08:00'
            ),
            (
                '2018-03-06 15:10:02',
                {
                    'every': [1, 'day'],
                    'at': {'hour': 12, 'minute': 0, 'second': 0},
                    'timezone': 'Asia/Shanghai'
                },
                '2018-03-07 12:00:00+08:00'
            ),
            (
                '2018-03-06 15:10:02',
                {
                    'every': [1, 'day'],
                    'at': {'hour': 2, 'minute': 0, 'second': 0},
                    'timezone': 'US/Pacific'
                },
                # 'US/Pacific' is 16 hours behind 'Asia/Shanghai'
                # after add one day to 2018-03-06 15:10:02, it is
                # 2018-03-07 15:10:02, but at 'US/Pacific', it is
                # 2018-03-06 23:10:02, need fire at
                # 2018-03-06 02:00:00, that is 2018-03-06 18:00:00+08:00
                '2018-03-06 18:00:00+08:00'
            ),
        )

        for last_fire, conf, expected_next_fire in cases:
            last_fire_date = timeutil.parse(last_fire, 'mysql')
            last_fire_ts = time.mktime(last_fire_date.timetuple())

            next_fire_time = jobscheduler.get_next_fire_time(conf, last_fire_ts)

            self.assertEqual(expected_next_fire, next_fire_time['string'])

    def test_exception(self):
        cases = (
            (
                '2018-03-06 15:08:11',
                {
                    'every': [1, 'hour'],
                    'at': {'hour': 14, 'second': 44},
                },
            ),
            (
                '2018-03-06 15:08:11',
                {
                    'every': [10, 'second'],
                    'at': {'second': 0},
                },
            ),
        )

        for last_fire, conf in cases:
            last_fire_date = timeutil.parse(last_fire, 'mysql')
            last_fire_ts = time.mktime(last_fire_date.timetuple())

            with self.assertRaises(Exception) as context:
                jobscheduler.get_next_fire_time(conf, last_fire_ts)

            self.assertIn('NextFireTimeError', repr(context.exception))
