#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import unittest

from pykit import modutil
from pykit import ututil

dd = ututil.dd

class TestModutil(unittest.TestCase):

    def setUp(self):

        sys.path.append(os.path.dirname(__file__))
        module_tree = [
                'root0',
                'root0.mod0',
                'root0.mod0.mod00',
                'root0.mod0.mod01',
                'root0.mod1',
                'root0.mod1.mod10',
                'root0.mod2',
                'root1',
                'root2',
                ]

        for module in module_tree:
            __import__(module)

    def tearDown(self):
        sys.path.remove(os.path.dirname(__file__))

    def test_submodules(self):

        test_cases = [
                (sys.modules['root0'], {
                                        'mod0': sys.modules['root0.mod0'],
                                        'mod1': sys.modules['root0.mod1'],
                                        'mod2': sys.modules['root0.mod2'], }, None),
                (sys.modules['root1'], {},                                    None),
                (sys.modules['root2'], None,                                  None),
                ({},                   None,                                  AttributeError),
            ]

        for root, rst_expected, error in test_cases:

            dd('case: ', root, rst_expected, error)

            try:
                rst = modutil.submodules(root)
            except error as e:
                self.assertEqual(type(e), error)
            else:
                dd('rst: ', rst)
                self.assertEqual(rst, rst_expected)

    def test_submodule_tree(self):

        test_cases = [
                ( sys.modules['root0'],
                  {
                    'mod0': {'module': sys.modules['root0.mod0'],
                            'children': {
                                'mod00': {'module': sys.modules['root0.mod0.mod00'],
                                          'children': {},
                                },
                                'mod01': {'module': sys.modules['root0.mod0.mod01'],
                                          'children': None,
                                },
                            },
                           },
                    'mod1': {'module': sys.modules['root0.mod1'],
                            'children': {
                                'mod10': {'module': sys.modules['root0.mod1.mod10'],
                                          'children': None,
                                },
                            },
                           },
                   'mod2': {'module': sys.modules['root0.mod2'],
                            'children': None,
                           },
                  },
                  None, ),
                ( sys.modules['root1'],
                  {},
                  None, ),
                ( sys.modules['root2'],
                  None,
                  None, ),
                ( {},
                  None,
                  AttributeError,),
                ]

        for root, rst_expected, error in test_cases:

            dd('case: ', root, rst_expected, error)

            try:
                rst = modutil.submodule_tree(root)
            except error as e:
                self.assertEqual(type(e), error)
            else:
                dd('rst: ', rst)
                self.assertEqual(rst, rst_expected)

    def test_submodule_leaf_tree(self):

        test_cases = [
                ( sys.modules['root0'],
                  {
                      'mod0': { 'mod00': {},
                                'mod01':sys.modules['root0.mod0.mod01'],
                              },
                      'mod1': { 'mod10': sys.modules['root0.mod1.mod10'], },
                      'mod2': sys.modules['root0.mod2'],
                  },
                  None, ),
                ( sys.modules['root1'],
                  {},
                  None, ),
                ( sys.modules['root2'],
                  None,
                  None, ),
                ( {},
                  None,
                  AttributeError, ),
                ]

        for root, rst_expected, error in test_cases:

            dd('case: ', root, rst_expected, error)

            try:
                rst = modutil.submodule_leaf_tree(root)
            except error as e:
                self.assertEqual(type(e), error)
            else:
                dd('rst: ', rst)
                self.assertEqual(rst, rst_expected)
