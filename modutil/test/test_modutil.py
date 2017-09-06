#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import unittest

from pykit import dictutil
from pykit import modutil

class TestModutil(unittest.TestCase):

    def setUp(self):

        sys.path.append(os.path.dirname(__file__))

        self.module_tree = {
                    'root0': {
                        'mod0': {
                            'mod00': {
                                    '__init__.py': True,
                                },
                            '__init__.py': True,
                            'mod01.py': False,
                        },
                        'mod1': {
                            '__init__.py': True,
                            'mod10.py': False,
                        },
                        '__init__.py': True,
                        'mod2.py': False,
                        },
                    'root1': {
                        '__init__.py': True,
                        },
                    'root2.py': False,
                }

        for _path, _init in dictutil.depth_iter(self.module_tree):
            if _init is True:
                mod_name = '.'.join(_path[:-1])
            else:
                mod_name = '.'.join(_path)[:-3]

            __import__(mod_name)

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

            try:
                rst = modutil.submodules(root)
            except error as e:
                self.assertEqual(type(e), error)
            else:
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

            try:
                rst = modutil.submodule_tree(root)
            except error as e:
                self.assertEqual(type(e), error)
            else:
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

            try:
                rst = modutil.submodule_leaf_tree(root)
            except error as e:
                self.assertEqual(type(e), error)
            else:
                self.assertEqual(rst, rst_expected)
