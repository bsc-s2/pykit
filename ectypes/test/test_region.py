#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import utfjson
from pykit import ututil
from pykit.ectypes import BlockDesc
from pykit.ectypes import BlockID
from pykit.ectypes import BlockNotInRegion
from pykit.ectypes import BlockAreadyInRegion
from pykit.ectypes import LevelOutOfBound
from pykit.ectypes import Region

dd = ututil.dd


class TestRegion(unittest.TestCase):

    def test_init(self):

        region_cases = [
            (
                {},
                {'idc': '', 'range': None, 'levels': []}
            ),
            (
                {'range': ['a', 'b'], 'idc': '.bei'},
                {'idc': '.bei', 'range': ['a', 'b'], 'levels': []}
            ),
            (
                {'levels': [[['a', 'b', BlockDesc()]], [['c', 'd', BlockDesc(size=1)]]]},
                {'idc': '', 'range': None, 'levels': [[['a', 'b', BlockDesc()]], [['c', 'd', BlockDesc(size=1)]]]}
            ),
            (
                {'range': ['a', 'z'], 'levels': [[['a', 'b', BlockDesc()], ['b', 'c', BlockDesc(size=2)]]]},
                {'idc': '', 'range': ['a', 'z'], 'levels': [[['a', 'b', BlockDesc()], ['b', 'c', BlockDesc(size=2)]]]}
            ),
        ]

        for case, excepted in region_cases:

            region = Region(case)
            self.assertEqual(excepted, region)

        region_cases_argkv = [
            (
                [[['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc(size=2)]]],
                {'idc': '', 'range': None, 'levels': [[['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc(size=2)]]]}
            ),
            (
                ['a', 'z'],
                {'idc': '', 'range': ['a', 'z'], 'levels': []}
            ),
            (
                [],
                {'idc': '', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc(size=2)]]]}
            ),
        ]

        region = Region(levels=region_cases_argkv[0][0])
        self.assertEqual(region_cases_argkv[0][1], region)

        region = Region(range=region_cases_argkv[1][0])
        self.assertEqual(region_cases_argkv[1][1], region)

        region = Region(levels=region_cases_argkv[0][0], range=region_cases_argkv[1][0])
        self.assertEqual(region_cases_argkv[2][1], region)

    def test_json(self):
        region = Region({'range': ['a', 'z'],
                                 'levels': [
            [['a', 'b', BlockDesc()],
             ['b', 'c', BlockDesc(size=2,
                                  block_id=BlockID('d1g0006300000001230101idc000c62d8736c72800020000000001'))]
             ]]})
        rst = utfjson.dump(region)
        expected = ('{"range": ["a", "z"], "levels": [[["a", "b", '
                    '{"is_del": 0, "range": null, "block_id": null, "size": 0}], '
                    '["b", "c", {"is_del": 0, "range": null, '
                    '"block_id": "d1g0006300000001230101idc000c62d8736c72800020000000001", "size": 2}]]], "idc": ""}')
        self.assertEqual(expected, rst)

        loaded = Region(utfjson.load(rst))
        self.assertEqual(region, loaded)

    def test_move_down(self):

        region_levels = [
            [
                ['aa', 'ee', BlockDesc(size=1)],
                ['hh', 'hz', BlockDesc(size=2)],
                ['pp', 'zz', BlockDesc(size=3)],
                ['zz', None, BlockDesc(size=4)]
            ],
            [
                ['cf', 'cz', BlockDesc(size=5)],
                ['mm', 'oo', BlockDesc(size=6)],
                ['oo', 'qq', BlockDesc(size=7)]
            ],
            [
                ['aa', 'bb', BlockDesc(size=8)],
                ['cc', 'cd', BlockDesc(size=9)],
                ['ee', 'ff', BlockDesc(size=10)]
            ],
            [
                ['aa', 'ab', BlockDesc(size=11)],
                ['az', 'bb', BlockDesc(size=12)],
                ['za', None, BlockDesc(size=13)]
            ],
            [
                ['d', 'fz', BlockDesc(size=14)]
            ],
        ]

        excepted_region_levels = [
            [
                ['aa', 'ee', BlockDesc(size=1)],
                ['ee', 'ff', BlockDesc(size=10)],
                ['hh', 'hz', BlockDesc(size=2)],
                ['mm', 'oo', BlockDesc(size=6)],
                ['pp', 'zz', BlockDesc(size=3)],
                ['zz', None, BlockDesc(size=4)]
            ],
            [
                ['aa', 'bb', BlockDesc(size=8)],
                ['cc', 'cd', BlockDesc(size=9)],
                ['cf', 'cz', BlockDesc(size=5)],
                ['d', 'fz', BlockDesc(size=14)],
                ['oo', 'qq', BlockDesc(size=7)],
                ['za', None, BlockDesc(size=13)]
            ],
            [
                ['aa', 'ab', BlockDesc(size=11)],
                ['az', 'bb', BlockDesc(size=12)]
            ],
        ]

        excepted_moved_blocks = [
            (1, 0, ['mm', 'oo', BlockDesc(size=6)]),
            (2, 1, ['aa', 'bb', BlockDesc(size=8)]),
            (2, 1, ['cc', 'cd', BlockDesc(size=9)]),
            (2, 0, ['ee', 'ff', BlockDesc(size=10)]),
            (3, 2, ['aa', 'ab', BlockDesc(size=11)]),
            (3, 2, ['az', 'bb', BlockDesc(size=12)]),
            (3, 1, ['za', None, BlockDesc(size=13)]),
            (4, 1, ['d',  'fz', BlockDesc(size=14)]),
        ]

        region = Region(levels=region_levels)
        moved_blocks = region.move_down()

        self.assertEqual(excepted_moved_blocks, moved_blocks)
        self.assertEqual(excepted_region_levels, region['levels'])

        region_levels = [
            [['aa', 'ee', BlockDesc(size=1)], ['ee', 'ff', BlockDesc(size=10)], ['hh', 'hz', BlockDesc(size=2)]],
            [['aa', 'yy', BlockDesc(size=8)]]
        ]

        region = Region(levels=region_levels)
        moved_blocks = region.move_down()

        self.assertEqual([], moved_blocks)
        self.assertEqual(region_levels, region['levels'])

    def test_find_merge(self):

        region_levels_cases = [
            [[[
                ['aa', 'ee', {'size': 8}],
                ['ee', 'ff', {'size': 16}],
                ['pp', 'zz', {'size': 8}],
                ['zz', None, {'size': 4}]
            ],
                [
                ['aa', 'pz', {'size': 4}],
                ['qq', 'zz', {'size': 8}]
            ]],
                (1, ['qq', 'zz', BlockDesc(size=8)], [['pp', 'zz', BlockDesc(size=8)]])],
            [[[
                ['aa', 'ee', {'size': 8}],
                ['ee', 'ff', {'size': 8}],
                ['hh', 'hz', {'size': 8}]
            ],
                [
                ['mm', 'yy', {'size': 8}]
            ]],
                None]
        ]

        for levels, excepted in region_levels_cases:
            region = Region(levels=levels)
            res = region.find_merge()

            self.assertEqual(excepted, res)

    def test_list_block_ids(self):

        bid1 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000001')
        bid2 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000002')
        bid3 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000003')
        bid4 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000004')
        bid5 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000005')
        bid6 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000006')

        region_levels = [
            [
                ['aa', 'ee', {'block_id': bid1}],
                ['hh', 'zz', {'block_id': bid2}]
            ],
            [
                ['ea', 'ff', {'block_id': bid4}],
                ['mm', 'yy', {'block_id': bid5}]
            ],
        ]

        cases = (
                (None, [bid1, bid2, bid4, bid5]),
                (bid3, [bid4, bid5]),
                (bid5, [bid5]),
                (bid6, []),
        )

        region = Region(levels=region_levels)

        for bid, excepted in cases:
            block_ids = region.list_block_ids(start_block_id=bid)
            self.assertEqual(excepted, block_ids)

    def test_replace_block_id(self):

        bid1 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000001')
        bid2 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000002')
        bid3 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000003')
        bid4 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000004')
        bid5 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000005')
        bid6 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000006')

        region_levels = [
            [['aa', 'ee', {'block_id': bid1}], ['hh', 'zz', {'block_id': bid2}]],
            [['ea', 'ff', {'block_id': bid4}], ['mm', 'yy', {'block_id': bid5}]],
        ]

        excepted_region_levels = [
            [['aa', 'ee', BlockDesc({'block_id': bid1})], ['hh', 'zz', BlockDesc({'block_id': bid2})]],
            [['ea', 'ff', BlockDesc({'block_id': bid3})], ['mm', 'yy', BlockDesc({'block_id': bid5})]],
        ]

        region = Region(levels=region_levels)

        region.replace_block_id(bid4, bid3)
        self.assertEqual(excepted_region_levels, region['levels'])

        self.assertRaises(BlockNotInRegion, region.replace_block_id, bid6, bid1)

    def test_add_block(self):

        region_cases = (
            (
                {},
                (['a', 'c'], BlockDesc(), None),
                {'idc': '', 'range': None, 'levels': [
                    [['a', 'c', BlockDesc()]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['b', 'c', BlockDesc(size=2)]],
                ]},
                (['c', 'd'], BlockDesc(), None),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['b', 'c', BlockDesc(size=2)]],
                    [['c', 'd', BlockDesc()]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                    [['b', 'c', BlockDesc(size=2)]],
                ]},
                (['c', 'd'], BlockDesc(), 0),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc()]],
                    [['b', 'c', BlockDesc(size=2)]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                    [['b', 'c', BlockDesc(size=2)]],
                ]},
                (['c', 'd'], BlockDesc(), 1),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                    [['b', 'c', BlockDesc(size=2)], ['c', 'd', BlockDesc()]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                    [['b', 'c', BlockDesc(size=2)]],
                ]},
                (['c', 'd'], BlockDesc(), 2),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                    [['b', 'c', BlockDesc(size=2)]],
                    [['c', 'd', BlockDesc()]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                    [['b', 'c', BlockDesc(size=2)]],
                ]},
                (['c', 'd'], BlockDesc(), 3),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                    [['b', 'c', BlockDesc(size=2)]],
                ]},
                LevelOutOfBound,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                    [['b', 'c', BlockDesc(size=2)]],
                ]},
                (['b', 'c'], BlockDesc(size=2), 2, True),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                    [['b', 'c', BlockDesc(size=2)]],
                ]},
                None
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                    [['b', 'c', BlockDesc(size=2)]],
                ]},
                (['b', 'c'], BlockDesc(size=2), 2, False),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                    [['b', 'c', BlockDesc(size=2)]],
                ]},
                BlockAreadyInRegion,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                    [['b', 'c', BlockDesc(size=2)]],
                ]},
                (None, BlockDesc(size=2), 2, False),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                    [['b', 'c', BlockDesc(size=2)]],
                ]},
                BlockAreadyInRegion,
            ),
        )

        for case, args, excepted, err in region_cases:
            region = Region(case)

            if err is not None:
                self.assertRaises(err, region.add_block, *args)
                continue

            region.add_block(*args)

            self.assertEqual(excepted, region)

    def test_delete_block(self):
        region_cases = (
            (
                {},
                (BlockDesc(size=2),),
                {},
                BlockNotInRegion,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], [
                        'b', 'c', BlockDesc(size=2)]],
                ]},
                (BlockDesc(size=3),),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], [
                        'b', 'c', BlockDesc(size=2)]],
                ]},
                BlockNotInRegion,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc()]],
                    [['b', 'c', BlockDesc(size=2)]],
                    [['c', 'd', BlockDesc(size=3)], ['d', 'e', BlockDesc()]],
                ]},
                (BlockDesc(size=2),),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc()]],
                    [['c', 'd', BlockDesc(size=3)], ['d', 'e', BlockDesc()]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc()]],
                    [['b', 'c', BlockDesc(size=2)]],
                    [['c', 'd', BlockDesc(size=3)], ['d', 'e', BlockDesc()]],
                ]},
                (BlockDesc(size=2), ['b', 'c'], 1, True),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc()]],
                    [['c', 'd', BlockDesc(size=3)], ['d', 'e', BlockDesc()]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc()]],
                    [['b', 'c', BlockDesc(size=2)]],
                    [['c', 'd', BlockDesc(size=3)], ['d', 'e', BlockDesc()]],
                ]},
                (BlockDesc(size=2), ['b', 'd'], 1, True),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc()]],
                    [['b', 'c', BlockDesc(size=2)]],
                    [['c', 'd', BlockDesc(size=3)], ['d', 'e', BlockDesc()]],
                ]},
                BlockNotInRegion,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc()]],
                    [['b', 'c', BlockDesc(size=2)]],
                    [['c', 'd', BlockDesc(size=3)], ['d', 'e', BlockDesc()]],
                ]},
                (BlockDesc(size=2), ['b', 'c'], 2, True),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc()]],
                    [['b', 'c', BlockDesc(size=2)]],
                    [['c', 'd', BlockDesc(size=3)], ['d', 'e', BlockDesc()]],
                ]},
                BlockNotInRegion,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc()]],
                    [['b', 'c', BlockDesc(size=2)]],
                    [['c', 'd', BlockDesc(size=3)], ['d', 'e', BlockDesc()]],
                ]},
                (BlockDesc(size=2), ['b', 'c'], 1, False),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)], ['c', 'd', BlockDesc()]],
                    [],
                    [['c', 'd', BlockDesc(size=3)], ['d', 'e', BlockDesc()]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', BlockDesc(size=1)]],
                ]},
                (BlockDesc(size=1),),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': []},
                None,
            ),
        )

        for case, args, excepted, err in region_cases:
            region = Region(case)

            if err is not None:
                self.assertRaises(err, region.delete_block, *args)
                continue

            region.delete_block(*args)

            self.assertEqual(excepted, region)

    def test_get_block_ids_by_needle_id(self):

        bid1 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000001')
        bid2 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000002')

        # each tuple in region_cases consists of
        # region
        # needle_id
        # result

        region_cases = [
            (
                {},
                'a',
                [],
            ),
            (
                {'range': ['a', 'e'], 'levels': [
                    [['a', 'b', {'block_id': bid1}], ['c', 'z', {'block_id': bid2}]]
                ]},
                'a',
                [bid1],
            ),
            (
                {'range': ['a', 'e'], 'levels': [
                    [['a', 'b', {'block_id': bid1}], ['c', 'z', {'block_id': bid2}]]
                ]},
                'b',
                [],
            ),
            (
                {'range': ['a', None], 'levels': [
                    [['a', 'b', {'block_id': bid1}], ['c', 'z', {'block_id': bid2}]]
                ]},
                'c',
                [bid2],
            ),
            (
                {'range': [None, 'e'], 'levels': [
                    [['a', 'b', {'block_id': bid1}], ['c', 'z', {'block_id': bid2}]]
                ]},
                'c',
                [bid2],
            ),
            (
                {'range': [None, None], 'levels': [
                    [['a', 'b', {'block_id': bid1}], ['c', 'z', {'block_id': bid2}]]
                ]},
                'a',
                [bid1],
            ),
            (
                {'range': ['a', 'e'], 'levels': [
                    [['a', 'b', {'block_id': bid1}], ['b', 'e', {'block_id': bid2}]]
                ]},
                'x',
                [],
            ),
            (
                {'range': ['a', 'e'], 'levels': [
                    [['a', 'b', {'block_id': bid1}], ['c', 'z', {'block_id': bid2}]]
                ]},
                'x',
                [],
            ),
            (
                {'range': ['a', 'z'], 'levels': [
                    [['a', 'b', {'block_id': bid1}]],
                    [['a', 'z', {'block_id': bid2}]]
                ]},
                'a',
                [bid2, bid1]
            ),
        ]

        for region_meta, needle_id, block_ids in region_cases:

            region = Region(region_meta)
            result = region.get_block_ids_by_needle_id(needle_id)
            self.assertEqual(block_ids, result)
