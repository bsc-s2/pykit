#!/usr/bin/env python2
# coding: utf-8

import unittest

from pykit import cluster
from pykit import ututil

dd = ututil.dd


class TestClusterRegion(unittest.TestCase):

    def test_init(self):

        region_cases = [
            [{},
                {'idc': None, 'range': [None, None], 'levels': []}],
            [{'range': ['a', 'b'], 'idc': '.bei'},
                {'idc': '.bei', 'range': ['a', 'b'], 'levels': []}],
            [{'levels': [[['a', 'b', 1]], [['c', 'd', 2]]]},
                {'idc': None, 'range': [None, None], 'levels': [[['a', 'b', 1]], [['c', 'd', 2]]]}],
            [{'range': ['a', 'z'], 'levels': [[['a', 'b', 1], ['b', 'c', 3]]]},
                {'idc': None, 'range': ['a', 'z'], 'levels': [[['a', 'b', 1], ['b', 'c', 3]]]}],
        ]

        for case, excepted in region_cases:

            region = cluster.Region(case)
            self.assertEqual(excepted, region)

    def test_move_down(self):

        region_levels = [
            [['aa', 'ee', 1], ['hh', 'hz', 2], ['pp', 'zz', 3], ['zz', None, 4]],
            [['cf', 'cz', 5], ['mm', 'oo', 6], ['oo', 'qq', 7]],
            [['aa', 'bb', 8], ['cc', 'cd', 9], ['ee', 'ff', 10]],
            [['aa', 'ab', 11], ['az', 'bb', 12], ['za', None, 13]],
            [['d', 'fz', 14]],
        ]

        excepted_region_levels = [
            [['aa', 'ee', 1], ['ee', 'ff', 10], ['hh', 'hz', 2], [
                'mm', 'oo', 6], ['pp', 'zz', 3], ['zz', None, 4]],
            [['aa', 'bb', 8], ['cc', 'cd', 9], ['cf', 'cz', 5], [
                'd', 'fz', 14], ['oo', 'qq', 7], ['za', None, 13]],
            [['aa', 'ab', 11], ['az', 'bb', 12]],
        ]

        excepted_moved_blocks = [
            (1, 0, ['mm', 'oo', 6]),
            (2, 1, ['aa', 'bb', 8]),
            (2, 1, ['cc', 'cd', 9]),
            (2, 0, ['ee', 'ff', 10]),
            (3, 2, ['aa', 'ab', 11]),
            (3, 2, ['az', 'bb', 12]),
            (3, 1, ['za', None, 13]),
            (4, 1, ['d', 'fz', 14]),
        ]

        region = cluster.Region(levels=region_levels)
        moved_blocks = region.move_down()

        self.assertEqual(excepted_moved_blocks, moved_blocks)
        self.assertEqual(excepted_region_levels, region['levels'])

        region_levels = [
            [['aa', 'ee', 1], ['ee', 'ff', 10], ['hh', 'hz', 2]],
            [['aa', 'yy', 8]]
        ]

        region = cluster.Region(levels=region_levels)
        moved_blocks = region.move_down()

        self.assertEqual([], moved_blocks)
        self.assertEqual(region_levels, region['levels'])

    def test_find_merge(self):

        region_levels_cases = [
            [
                [
                    [['aa', 'ee', {'size': 8}], ['ee', 'ff', {'size': 16}], [
                        'pp', 'zz', {'size': 8}], ['zz', None, {'size': 4}]],
                    [['aa', 'pz', {'size': 4}], ['qq', 'zz', {'size': 8}]]
                ],
                (1, ['qq', 'zz', {'size': 8}], [['pp', 'zz', {'size': 8}]])
            ],
            [
                [
                    [['aa', 'ee', {'size': 8}], ['ee', 'ff', {
                        'size': 8}], ['hh', 'hz', {'size': 8}]],
                    [['mm', 'yy', {'size': 8}]]
                ],
                None
            ]
        ]

        for levels, excepted in region_levels_cases:
            region = cluster.Region(levels=levels)
            res = region.find_merge()

            self.assertEqual(excepted, res)
