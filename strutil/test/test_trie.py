#!/usr/bin/env python2
# coding: utf-8

import os
import unittest

from pykit import dictutil
from pykit import fsutil
from pykit import strutil
from pykit import ututil

dd = ututil.dd

this_base = os.path.dirname(__file__)

class TestTrie(unittest.TestCase):

    def setUp(self):
        self.strs = (
                'abc',
                'abcdef',
                'abcdeg',
                'abcdfg',
                'abd',
                'abe',
                'axy',
                'b11',
                'b12',
                'b123',
                'b14',
        )

    def test_trie_whole_string(self):

        t = strutil.make_trie(self.strs, node_max_num=3)

        dd('trie:')
        dd(str(t))

        self.assertEqual(len(self.strs), t.n)

        # only whole strings
        for ks, v in dictutil.depth_iter(t, is_allowed=lambda ks, v: strutil.EOL in v):

            self.assertEqual(1, v[strutil.EOL].n)

            s = ''.join(ks)
            self.assertTrue(s in self.strs)

    def test_trie_prefix_count(self):

        t = strutil.make_trie(self.strs, node_max_num=3)

        dd('==== trie:')
        dd(str(t))

        # all prefixes, might be also a whole string.
        for ks, v in dictutil.depth_iter(t, is_allowed=lambda ks, v: v.char != strutil.EOL):

            dd('==== got keys:', ks, 'sub trie:')
            dd(v)

            prefix = ''.join(ks)
            expected = len([x
                            for x in self.strs
                            if x.startswith(prefix)])

            key_path = '.'.join(ks)
            subtrie = dictutil.get(t, key_path, default=-1)
            rst = subtrie.n

            dd('prefix:', prefix, 'trie key_path:', key_path, 'sub trie:')
            dd(str(subtrie))
            dd('expected:', expected)
            dd('rst:', rst)

            self.assertEqual(expected, rst)

            # Leaf node number limit
            if len(v) == 0:
                self.assertLessEqual(rst, 3)


    def test_node_max_num(self):

        t = strutil.make_trie(self.strs, node_max_num=1)

        for ks, v in dictutil.depth_iter(t, empty_leaf=True):

            key_path = '.'.join(ks)
            subtrie = dictutil.get(t, key_path, default=-1)

            self.assertEqual(1, subtrie.n)

        # all in one node

        t = strutil.make_trie(self.strs, node_max_num=10000)

        dd()
        dd(str(t))

        self.assertEqual(len(self.strs), t.n)
        self.assertEqual(0, len(t))

    def test_sharding(self):

        with open(os.path.join(this_base, 'words')) as f:
            lines = f.readlines()
            lines = [x.strip() for x in lines]

        _size, _accuracy = 200, 20

        rst = strutil.sharding(lines, size=_size, accuracy=_accuracy)

        expected = [
                (''      , 209, ),
                ('M'     , 202, ),
                ('TestU' , 202, ),
                ('br'    , 202, ),
                ('dc'    , 201, ),
                ('exi'   , 202, ),
                ('inf'   , 204, ),
                ('may'   , 205, ),
                ('pf'    , 200, ),
                ('rew'   , 208, ),
                ('suc'   , 204, ),
                ('wh'    , 56,  ),
        ]

        for i, (start, size) in enumerate(rst):
            dd('{start:<10} {size:>20}'.format(start=start, size=size))
            self.assertEqual(expected[i], (start, size))

        # general cases

        cases = (
            (1, 1),
            (20, 1),
            (20, 5),
            (200, 20),
            (200, 100),
        )

        for _size, _accuracy in cases:

            dd('size: {_size}, accuracy: {_accuracy}'.format(_size=_size, _accuracy=_accuracy))

            rst = strutil.sharding(lines, size=_size, accuracy=_accuracy)

            tot = 0
            prev = None
            for i, (start, size) in enumerate(rst):

                dd('{start:<10} {size:>20}'.format(start=start, size=size))

                # the last shard might have less items
                if i < len(rst) - 1:
                    nxt = rst[i+1][0]
                    self.assertLessEqual(_size, size)
                    self.assertLessEqual(size, _size + _accuracy)
                    self.assertEqual(len([x for x in lines
                                          if x >= start and x < nxt ]),
                                     size)
                else:
                    self.assertLessEqual(size, _size)
                    self.assertEqual(len([x for x in lines
                                          if x >= start ]),
                                     size)

                tot += size

            self.assertEqual(len(lines), tot)
