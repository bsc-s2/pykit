
import logging

from pykit import rangeset

logger = logging.getLogger(__name__)


def load(gtid_set_str):

    # https://dev.mysql.com/doc/refman/5.6/en/replication-gtids-concepts.html
    #
    # gtid_set:
    #     uuid_set [, uuid_set] ...
    #     | ''
    # uuid_set:
    #     uuid:interval[:interval]...
    # uuid:
    #     hhhhhhhh-hhhh-hhhh-hhhh-hhhhhhhhhhhh
    # h:
    #     [0-9|A-F]
    # interval:
    #     n[-n]
    #     (n >= 1)
    #
    # <uuid>:<start>-<end>:<start-2>-<end2>,\n
    # <uuid>:<start>,\n
    # <uuid>:<start>-<end>,\n
    # ...
    #
    # 1fcc256b-84b0-11e6-acaf-00163e03bb03:1-326,\n
    # xxxxxxxx-84b0-11e6-acaf-00163e03bb03:1

    # {
    #   <uuid>: IntIncRangeSet([[1, 1], [10, 30]]),
    #   <uuid>: IntIncRangeSet([[1, 1], [10, 30]]),
    #   ...
    # }
    _set = gtid_set_str.split(',')

    logger.debug('gtid set: ' + repr(_set))

    gtid_set = {}

    for uuid_set in _set:

        uuid_set = uuid_set.strip()

        uuid_intervals = uuid_set.split(':')
        uuid = uuid_intervals[0]
        intervals = uuid_intervals[1:]

        gtid_set[uuid] = []

        ranges = []

        for interval in intervals:

            interval = interval.split('-')

            # single transaction range is just xxx:1, not xxx:1-2
            if len(interval) == 1:
                interval = [interval[0], interval[0]]

            interval = (int(interval[0]), int(interval[1]))

            ranges.append(interval)

        gtid_set[uuid] = rangeset.IntIncRangeSet(ranges)

    logger.debug('gtid_set parsed: ' + repr(gtid_set))

    return gtid_set


def dump(gtid_set, line_break='\n'):

    rst = []

    for uuid, ranges in gtid_set.items():
        uuid_set_str = [uuid, ]
        for rng in ranges:
            if rng.length() == 1:
                itv_str = '{0}'.format(rng[0])
            else:
                itv_str = '{0}-{1}'.format(*rng)

            uuid_set_str.append(itv_str)

        rst.append(':'.join(uuid_set_str))

    rst.sort()
    return (',' + line_break).join(rst)


def compare(a, b):

    rst = {
        'onlyleft': {
            'length': 0,
            'gtidset': {},
        },
        'onlyright': {
            'length': 0,
            'gtidset': {},
        },
    }

    for uuid, intervals in a.items():

        ll = rangeset.substract(intervals, b.get(uuid, rangeset.IntIncRangeSet([])))
        if ll.length() > 0:
            rst['onlyleft']['gtidset'][uuid] = ll
            rst['onlyleft']['length'] += ll.length()

    for uuid, intervals in b.items():

        ll = rangeset.substract(intervals, a.get(uuid, rangeset.IntIncRangeSet([])))
        if ll.length() > 0:
            rst['onlyright']['gtidset'][uuid] = ll
            rst['onlyright']['length'] += ll.length()

    return rst
