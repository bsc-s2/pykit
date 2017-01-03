#!/usr/bin/env python2
# coding: utf-8

import unittest

import dictutil


class TestDictIter(unittest.TestCase):

    def test_depth_iter_default(self):

        cases = (
            ({}, []),
            ({'k1': 'v1'}, [(['k1'], 'v1')]),
            ({'k1': 'v1', 'k2': 'v2'}, [(['k2'], 'v2'), (['k1'], 'v1')]),
            ({'k1': {'k11': 'v11'}, 'k2': 'v2'},
             ([(['k2'], 'v2'), (['k1', 'k11'], 'v11')]),
             )
        )

        for _in, _out in cases:

            idx = 0

            for rst in dictutil.depth_iter(_in):
                self.assertEqual(
                    _out[idx],
                    rst,
                    ('input: {_in}, output: {rst}, expected: {_out}').format(
                        _in=repr(_in),
                        _out=repr(rst),
                        rst=repr(_out[idx])
                    )
                )

                idx = idx + 1


    def test_depth_iter_ks(self):

        idx = 0
        ks = ['mykey']

        _in = {'k1': {'k11': 'v11'}, 'k2': 'v2'}
        _out = [(['mykey', 'k2'], 'v2'), (['mykey', 'k1', 'k11'], 'v11')]
        _mes = 'test argument ks in dictutil.dict_depth_iter()'

        for rst in dictutil.depth_iter(_in, ks=ks):
            self.assertEqual(
                _out[idx],
                rst,
                ('input: {_in}, output: {rst}, expected: {_out},'
                 'message: {_mes}').format(
                     _in=repr(_in),
                     _out=repr(rst),
                     rst=repr(_out[idx]),
                     _mes=_mes
                )
            )

            idx = idx + 1


    def test_depth_iter_maxdepth(self):

        idx = 0

        _in = {'k1': {'k11': {'k111': {'k1111': 'v1111'}}}}
        _out = [(['k1'], {'k11': {'k111': {'k1111': 'v1111'}}}),
                (['k1', 'k11'], {'k111': {'k1111': 'v1111'}}),
                (['k1', 'k11', 'k111'], {'k1111': 'v1111'}),
                (['k1', 'k11', 'k111', 'k1111'], 'v1111')
                ]

        for depth in range(1, 5):
            for rst in dictutil.depth_iter(_in, maxdepth=depth):
                self.assertEqual(
                    _out[idx],
                    rst,
                    'input:: {_in}, output: {rst}, expected: {_out}'.format(
                        _in=repr(_in),
                        rst=repr(rst),
                        _out=repr(_out[idx])
                    )
                )

            idx = idx + 1


    def test_depth_iter_get_mid(self):

        idx = 0

        _in = {'k1': {'k11': {'k111': {'k1111': 'v1111'}}}}
        _out = [(['k1'], {'k11': {'k111': {'k1111': 'v1111'}}}),
                (['k1', 'k11'], {'k111': {'k1111': 'v1111'}}),
                (['k1', 'k11', 'k111'], {'k1111': 'v1111'}),
                (['k1', 'k11', 'k111', 'k1111'], 'v1111')
                ]

        for rst in dictutil.depth_iter(_in, get_mid=True):
            self.assertEqual(
                _out[idx],
                rst)

            idx = idx + 1


    def test_breadth_iter_default(self):

        cases = (
            ({}, []),
            ({'k1': 'v1'}, [(['k1'], 'v1')]),
            ({'k1': 'v1', 'k2': 'v2'}, [(['k2'], 'v2'), (['k1'], 'v1')]),
            ({'k1': {'k11': 'v11'}, 'k2': 'v2'},
             ([(['k2'], 'v2'),
               (['k1'], {'k11': 'v11'}),
               (['k1', 'k11'], 'v11')
               ])
             )
        )

        for _in, _out in cases:

            idx = 0

            for rst in dictutil.breadth_iter(_in):
                self.assertEqual(
                    _out[idx],
                    rst,
                    ('input: {_in}, output: {rst}, expected: {_out}').format(
                        _in=repr(_in),
                        _out=repr(rst),
                        rst=repr(_out[idx]),
                    )
                )

                idx = idx + 1
