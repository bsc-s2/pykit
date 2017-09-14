import json
import logging
import unittest

from pykit import mysqlutil
from pykit import ututil

dd = ututil.dd

logger = logging.getLogger(__name__)


class TestGtidset(unittest.TestCase):

    maxDiff = 1024

    def test_load_dump(self):

        gtidset_str_a = '\n'.join([
            '103a96e9-a030-11e6-b082-a0369fabbda4:1-20:25,',
            '3f96fb31-6a18-11e6-bd74-a0369fabbdb8:1-30,',
            '630b605d-9ec7-11e6-aae9-a0369fabbdb8:1-90,',
            '83e2adaf-9c37-11e6-9d6e-a0369fb6f7b4:1-70',
        ])

        gtidset_str_b = '\n'.join([
            '103a96e9-a030-11e6-b082-a0369fabbda4:1-20:26,',
            # '3f96fb31-6a18-11e6-bd74-a0369fabbdb8:1-30,',
            '630b605d-9ec7-11e6-aae9-a0369fabbdb8:5-90,',
            '83e2adaf-9c37-11e6-9d6e-a0369fb6f7b4:1-60,',
            'f4ebb415-a801-11e6-9079-a0369fb4eb00:1-80',
        ])

        expected = {
            '103a96e9-a030-11e6-b082-a0369fabbda4': [[1, 20], [25, 25]],
            '3f96fb31-6a18-11e6-bd74-a0369fabbdb8': [[1, 30]],
            '630b605d-9ec7-11e6-aae9-a0369fabbdb8': [[1, 90]],
            '83e2adaf-9c37-11e6-9d6e-a0369fb6f7b4': [[1, 70]],
        }

        dd()
        dd(gtidset_str_a)

        dd('test load')

        gs_a = mysqlutil.gtidset.load(gtidset_str_a)
        dd('gs_a:', gs_a)
        self.assertEqual(expected, gs_a)

        dd('test dump')

        gs_str_a = mysqlutil.gtidset.dump(gs_a)
        dd('gs_str_a:', gs_str_a)
        self.assertEqual(gtidset_str_a, gs_str_a)
        self.assertEqual(gtidset_str_a.replace('\n', ''),
                         mysqlutil.gtidset.dump(gs_a, line_break=''))

        dd('test compare gtidset')

        expected_cmp_rst = {
            "onlyleft": {
                'length': 45,
                'gtidset': {
                    "103a96e9-a030-11e6-b082-a0369fabbda4": [[25, 25]],
                    "3f96fb31-6a18-11e6-bd74-a0369fabbdb8": [[1, 30]],
                    "630b605d-9ec7-11e6-aae9-a0369fabbdb8": [[1, 4]],
                    "83e2adaf-9c37-11e6-9d6e-a0369fb6f7b4": [[61, 70]]
                },
            },
            "onlyright": {
                'length': 81,
                'gtidset': {
                    "103a96e9-a030-11e6-b082-a0369fabbda4": [[26, 26]],
                    "f4ebb415-a801-11e6-9079-a0369fb4eb00": [[1, 80]]
                },
            },
        }

        gs_b = mysqlutil.gtidset.load(gtidset_str_b)

        cmp_rst = mysqlutil.gtidset.compare(gs_a, gs_b)
        dd(json.dumps(expected_cmp_rst, indent=2))
        dd(json.dumps(cmp_rst, indent=2))

        self.assertEqual(expected_cmp_rst, cmp_rst)
