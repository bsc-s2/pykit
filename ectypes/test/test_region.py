#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import utfjson
from pykit import ututil
from pykit.ectypes import BlockID
from pykit.ectypes import BlockNotInRegion
from pykit.ectypes import BlockAreadyInRegion
from pykit.ectypes import LevelOutOfBound
from pykit.ectypes import Region

dd = ututil.dd

tbid0 = BlockID('d0g0006300000001230101idc000c62d8736c72800020000000000')
tbid1 = BlockID('d0g0006300000001230101idc000c62d8736c72800020000000001')
tbid2 = BlockID('d0g0006300000001230101idc000c62d8736c72800020000000002')
tbid3 = BlockID('d0g0006300000001230101idc000c62d8736c72800020000000003')
tbid4 = BlockID('d0g0006300000001230101idc000c62d8736c72800020000000004')
tbid5 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000005')
tbid6 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000006')
tbid7 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000007')
tbid8 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000008')
tbid9 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000009')
tbid10 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000010')
tbid11 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000011')
tbid12 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000012')
tbid13 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000013')
tbid14 = BlockID('d1g0006300000001230101idc000c62d8736c72800020000000014')


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
                {'levels': [[['a', 'b', tbid1]], [['c', 'd', tbid2]]]},
                {'idc': '', 'range': None, 'levels': [[['a', 'b', tbid1]], [['c', 'd', tbid2]]]}
            ),
            (
                {'range': ['a', 'z'], 'levels': [[['a', 'b', tbid1], ['b', 'c', tbid2]]]},
                {'idc': '', 'range': ['a', 'z'], 'levels': [[['a', 'b', tbid1], ['b', 'c', tbid2]]]}
            ),
        ]

        for case, excepted in region_cases:

            region = Region(case)
            self.assertEqual(excepted, region)

        region_cases_argkv = [
            (
                [[['a', 'b', tbid1], ['c', 'd', tbid2]]],
                {'idc': '', 'range': None, 'levels': [[['a', 'b', tbid1], ['c', 'd', tbid2]]]}
            ),
            (
                ['a', 'z'],
                {'idc': '', 'range': ['a', 'z'], 'levels': []}
            ),
            (
                [],
                {'idc': '', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'd', tbid2]]]}
            ),
        ]

        region = Region(levels=region_cases_argkv[0][0])
        self.assertEqual(region_cases_argkv[0][1], region)

        region = Region(range=region_cases_argkv[1][0])
        self.assertEqual(region_cases_argkv[1][1], region)

        region = Region(levels=region_cases_argkv[0][0], range=region_cases_argkv[1][0])
        self.assertEqual(region_cases_argkv[2][1], region)

    def test_json(self):
        region = Region({
                'range': ['a', 'z'],
                'levels': [
                    [['a', 'b', tbid1], ['b', 'c', tbid2]]
                ]})

        rst = utfjson.dump(region)

        expected = ('{"range": ["a", "z"], "levels": '
                    '[[["a", "b", "' + tbid1 + '"], ["b", "c", "' + tbid2 + '"]]], "idc": ""}')

        self.assertEqual(utfjson.load(expected), region)
        self.assertEqual(region, Region(utfjson.load(rst)))

    def test_move_down(self):

        region_levels = [
            [
                ['aa', 'ee', tbid1],
                ['hh', 'hz', tbid2],
                ['pp', 'zz', tbid3],
                ['zz', None, tbid4]
            ],
            [
                ['cf', 'cz', tbid5],
                ['mm', 'oo', tbid6],
                ['oo', 'qq', tbid7]
            ],
            [
                ['aa', 'bb', tbid8],
                ['cc', 'cd', tbid9],
                ['ee', 'ff', tbid10]
            ],
            [
                ['aa', 'ab', tbid11],
                ['az', 'bb', tbid12],
                ['za', None, tbid13]
            ],
            [
                ['d', 'fz', tbid14]
            ],
        ]

        excepted_region_levels = [
            [
                ['aa', 'ee', tbid1],
                ['ee', 'ff', tbid10],
                ['hh', 'hz', tbid2],
                ['mm', 'oo', tbid6],
                ['pp', 'zz', tbid3],
                ['zz', None, tbid4]
            ],
            [
                ['aa', 'bb', tbid8],
                ['cc', 'cd', tbid9],
                ['cf', 'cz', tbid5],
                ['d', 'fz', tbid14],
                ['oo', 'qq', tbid7],
                ['za', None, tbid13]
            ],
            [
                ['aa', 'ab', tbid11],
                ['az', 'bb', tbid12]
            ],
        ]

        excepted_moved_blocks = [
            (1, 0, ['mm', 'oo', tbid6]),
            (2, 1, ['aa', 'bb', tbid8]),
            (2, 1, ['cc', 'cd', tbid9]),
            (2, 0, ['ee', 'ff', tbid10]),
            (3, 2, ['aa', 'ab', tbid11]),
            (3, 2, ['az', 'bb', tbid12]),
            (3, 1, ['za', None, tbid13]),
            (4, 1, ['d',  'fz', tbid14]),
        ]

        region = Region(levels=region_levels)
        moved_blocks = region.move_down()

        self.assertEqual(excepted_moved_blocks, moved_blocks)
        self.assertEqual(excepted_region_levels, region['levels'])

        region_levels = [
            [
                ['aa', 'ee', tbid1],
                ['ee', 'ff', tbid10],
                ['hh', 'hz', tbid2],
            ],
            [['aa', 'yy', tbid8]]
        ]

        region = Region(levels=region_levels)
        moved_blocks = region.move_down()

        self.assertEqual([], moved_blocks)
        self.assertEqual(region_levels, region['levels'])

    def test_list_block_ids(self):

        region_levels = [
            [
                ['aa', 'ee', tbid1],
                ['hh', 'zz', tbid2]
            ],
            [
                ['ea', 'ff', tbid4],
                ['mm', 'yy', tbid5]
            ],
        ]

        cases = (
                (None, [tbid1, tbid2, tbid4, tbid5]),
                (tbid3, [tbid4, tbid5]),
                (tbid5, [tbid5]),
                (tbid6, []),
        )

        region = Region(levels=region_levels)

        for bid, excepted in cases:
            block_ids = region.list_block_ids(start_block_id=bid)
            self.assertEqual(excepted, block_ids)

    def test_replace_block_id(self):

        region_levels = [
            [['aa', 'ee', tbid1], ['hh', 'zz', tbid2]],
            [['ea', 'ff', tbid4], ['mm', 'yy', tbid5]],
        ]

        excepted_region_levels = [
            [['aa', 'ee', tbid1], ['hh', 'zz', tbid2]],
            [['ea', 'ff', tbid3], ['mm', 'yy', tbid5]],
        ]

        region = Region(levels=region_levels)

        region.replace_block_id(tbid4, tbid3)
        self.assertEqual(excepted_region_levels, region['levels'])

        self.assertRaises(BlockNotInRegion, region.replace_block_id, tbid6, tbid1)

    def test_add_block(self):

        region_cases = (
            (
                {},
                (['a', 'c'], tbid0, None),
                {'idc': '', 'range': None, 'levels': [
                    [['a', 'c', tbid0]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['b', 'c', tbid2]],
                ]},
                (['c', 'd'], tbid0, None),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['b', 'c', tbid2]],
                    [['c', 'd', tbid0]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['b', 'c', tbid2]],
                ]},
                (['c', 'd'], tbid0, 0),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'd', tbid0]],
                    [['b', 'c', tbid2]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['b', 'c', tbid2]],
                ]},
                (['c', 'd'], tbid0, 1),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['b', 'c', tbid2], ['c', 'd', tbid0]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['b', 'c', tbid2]],
                ]},
                (['c', 'd'], tbid0, 2),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['b', 'c', tbid2]],
                    [['c', 'd', tbid0]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['b', 'c', tbid2]],
                ]},
                (['c', 'd'], tbid0, 3),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['b', 'c', tbid2]],
                ]},
                LevelOutOfBound,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['b', 'c', tbid2]],
                ]},
                (['b', 'c'], tbid2, 2, True),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['b', 'c', tbid2]],
                ]},
                None
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['b', 'c', tbid2]],
                ]},
                (['b', 'c'], tbid2, 2, False),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['b', 'c', tbid2]],
                ]},
                BlockAreadyInRegion,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['b', 'c', tbid2]],
                ]},
                (None, tbid2, 2, False),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['b', 'c', tbid2]],
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
                (tbid2,),
                {},
                BlockNotInRegion,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], [
                        'b', 'c', tbid2]],
                ]},
                (tbid3,),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], [
                        'b', 'c', tbid2]],
                ]},
                BlockNotInRegion,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'd', tbid0]],
                    [['b', 'c', tbid2]],
                    [['c', 'd', tbid3], ['d', 'e', tbid0]],
                ]},
                (tbid2,),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'd', tbid0]],
                    [['c', 'd', tbid3], ['d', 'e', tbid0]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'd', tbid0]],
                    [['b', 'c', tbid2]],
                    [['c', 'd', tbid3], ['d', 'e', tbid0]],
                ]},
                (tbid2, ['b', 'c'], 1, True),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'd', tbid0]],
                    [['c', 'd', tbid3], ['d', 'e', tbid0]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'd', tbid0]],
                    [['b', 'c', tbid2]],
                    [['c', 'd', tbid3], ['d', 'e', tbid0]],
                ]},
                (tbid2, ['b', 'd'], 1, True),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'd', tbid0]],
                    [['b', 'c', tbid2]],
                    [['c', 'd', tbid3], ['d', 'e', tbid0]],
                ]},
                BlockNotInRegion,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'd', tbid0]],
                    [['b', 'c', tbid2]],
                    [['c', 'd', tbid3], ['d', 'e', tbid0]],
                ]},
                (tbid2, ['b', 'c'], 2, True),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'd', tbid0]],
                    [['b', 'c', tbid2]],
                    [['c', 'd', tbid3], ['d', 'e', tbid0]],
                ]},
                BlockNotInRegion,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'd', tbid0]],
                    [['b', 'c', tbid2]],
                    [['c', 'd', tbid3], ['d', 'e', tbid0]],
                ]},
                (tbid2, ['b', 'c'], 1, False),
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'd', tbid0]],
                    [],
                    [['c', 'd', tbid3], ['d', 'e', tbid0]],
                ]},
                None,
            ),
            (
                {'idc': 'test', 'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                ]},
                (tbid1,),
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
                    [['a', 'b', tbid1], ['c', 'z', tbid2]]
                ]},
                'a',
                [tbid1],
            ),
            (
                {'range': ['a', 'e'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'z', tbid2]]
                ]},
                'b',
                [],
            ),
            (
                {'range': ['a', None], 'levels': [
                    [['a', 'b', tbid1], ['c', 'z', tbid2]]
                ]},
                'c',
                [tbid2],
            ),
            (
                {'range': [None, 'e'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'z', tbid2]]
                ]},
                'c',
                [tbid2],
            ),
            (
                {'range': [None, None], 'levels': [
                    [['a', 'b', tbid1], ['c', 'z', tbid2]]
                ]},
                'a',
                [tbid1],
            ),
            (
                {'range': ['a', 'e'], 'levels': [
                    [['a', 'b', tbid1], ['b', 'e', tbid2]]
                ]},
                'x',
                [],
            ),
            (
                {'range': ['a', 'e'], 'levels': [
                    [['a', 'b', tbid1], ['c', 'z', tbid2]]
                ]},
                'x',
                [],
            ),
            (
                {'range': ['a', 'z'], 'levels': [
                    [['a', 'b', tbid1]],
                    [['a', 'z', tbid2]]
                ]},
                'a',
                [tbid2, tbid1]
            ),
        ]

        for region_meta, needle_id, block_ids in region_cases:

            region = Region(region_meta)
            result = region.get_block_ids_by_needle_id(needle_id)
            self.assertEqual(block_ids, result)
