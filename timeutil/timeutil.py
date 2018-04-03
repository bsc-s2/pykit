#!/usr/bin/env python2
# coding: utf-8

import calendar
import datetime
import time
import types

import pytz
import tzlocal

formats = {
    'default':        '%a, %d %b %Y %H:%M:%S UTC',
    'utc':            '%a, %d %b %Y %H:%M:%S UTC',
    'iso':            '%Y-%m-%dT%H:%M:%S.000Z',
    'archive':        '%Y%m%d-%H',
    'compact':        '%Y%m%d-%H%M%S',
    'daily':          '%Y-%m-%d',
    'daily_compact':  '%Y%m%d',
    'mysql':          '%Y-%m-%d %H:%M:%S',
    'nginxaccesslog': "%d/%b/%Y:%H:%M:%S",
    'nginxerrorlog':  "%Y/%m/%d %H:%M:%S",
}

ts_length = {
    's':  10,
    'ms': 13,
    'us': 16,
    'ns': 19,
}


def parse(time_str, fmt_key, timezone=None):
    dt = datetime.datetime.strptime(time_str, _get_format(fmt_key))
    if timezone is not None:
        tz = pytz.timezone(timezone)
        dt = tz.localize(dt)

    return dt


def format(dt, fmt_key):
    return dt.strftime(_get_format(fmt_key))


def format_ts(ts, fmt_key, utc=True):
    dt = ts_to_datetime(ts, utc)
    return format(dt, fmt_key)


def _get_format(fmt_key):
    return formats.get(fmt_key) or fmt_key


def utc_datetime_to_ts(dt):
    return calendar.timegm(dt.timetuple())


def datetime_to_ts(dt):
    epoch_dt = datetime.datetime.fromtimestamp(0, tz=pytz.utc)

    if not hasattr(dt, 'tzinfo') or dt.tzinfo is None:
        local_tz = tzlocal.get_localzone()
        dt = local_tz.localize(dt)

    delta = dt - epoch_dt
    ts = delta.total_seconds()

    return ts


def ts_to_datetime(ts, utc=True):
    if utc:
        return datetime.datetime.utcfromtimestamp(ts)
    else:
        return datetime.datetime.fromtimestamp(ts)


def ts():
    return int(time.time())


def ms():
    return int(time.time() * 1000)


def us():
    return int(time.time() * (1000 ** 2))


def ns():
    return int(time.time() * (1000 ** 3))


def ms_to_ts(ms):
    return ms / 1000


def us_to_ts(us):
    return us / (1000 ** 2)


def ns_to_ts(ns):
    return ns / (1000 ** 3)


def to_sec(v):
    """
    Convert millisecond, microsecond or nanosecond to second.

    ms_to_ts, us_to_ts, ns_to_ts are then deprecated.
    """

    v = float(str(v))

    if (type(v) != types.FloatType
            or v < 0):
        raise ValueError('invalid time to convert to second: {v}'.format(v=v))

    l = len(str(int(v)))

    if l == 10:
        return int(v)
    elif l == 13:
        return int(v / 1000)
    elif l == 16:
        return int(v / (1000**2))
    elif l == 19:
        return int(v / (1000**3))
    else:
        raise ValueError(
            'invalid time length, not 10, 13, 16 or 19: {v}'.format(v=v))


def is_timestamp(string, unit=None):

    string = str(string)

    if not string.isdigit():
        return False

    if unit is None:
        return len(string) in ts_length.values()

    if unit in ts_length:
        return len(string) == ts_length[unit]

    return False
