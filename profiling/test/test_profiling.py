#!/usr/bin/env python2
# coding: utf-8

import unittest

import profiling


class TestPP(unittest.TestCase):

    def test_make_refby(self):

        cases = (
                ({},
                 {},
                ),

                ({1:{2:True}},
                 {2:{1:True}},
                ),

                ({1:{2:True, 3:True}},
                 {2:{1:True}, 3:{1:True}},
                ),

                ({1:{2:True}, 2:{3:True}},
                 {2:{1:True}, 3:{2:True}},
                ),

                ({1:{2:True}, 2:{3:True}, 3:{1:True}},
                 {3:{2:True}, 1:{3:True}, 2:{1:True}},
                )
        )

        for ref, refby in cases:
            rst = profiling.make_refby(ref)

            self.assertEqual(refby, rst, repr((ref, refby)))


    def test_find_cycles(self):

        cases = (
                ({},
                 [],
                ),

                ({1:{2:True}},
                 [],
                ),

        )

        for ref, cycles in cases:
            rst = profiling.find_cycles(ref)

            self.assertEqual(cycles, rst, repr((ref, cycles, 'rst:', rst)))

