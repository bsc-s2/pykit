import logging
import unittest

from pykit import rangeset
from pykit import ututil

dd = ututil.dd

logger = logging.getLogger(__name__)


class TestRange(unittest.TestCase):

    def test_has(self):
        cases = (
                ([None, None], 0, True),
                ([None, None], 1, True),
                ([None, 1],    0, True),
                ([None, 1],    1, False),
                ([None, 1],    2, False),
                ([1,    None], 0, False),
                ([1,    None], 1, True),
                ([1,    None], 2, True),
                ([1,    3],    0, False),
                ([1,    3],    1, True),
                ([1,    3],    2, True),
                ([1,    3],    3, False),
                ([1,    3],    4, False),
        )

        dd()
        for rng, val, expected in cases:
            dd('case:', rng, val, expected)

            rng = rangeset.Range(*rng)
            rst = rng.has(val)

            self.assertEqual(expected, rst)

    def test_element_type_detection(self):
        cases = (
                (None, None, int),
                (1,    None, int),
                (None, 1,    int),
                (1,    1,    int),
                (None, 1.0,  float),
                (1.0,  None, float),
                (1.0,  1.0,  float),
                ('',   None, str),
                (None, '',   str),
                ('',   '',   str),
                (None, (),   tuple),
                ((),   None, tuple),
                ((),   (),   tuple),
                (None, [],   list),
                ([],   None, list),
                ([],   [],   list),
        )
        dd()
        for l, r, expected in cases:
            a = rangeset.Range(l, r)
            self.assertEqual(expected, a.element_type)


class TestRangeSet(unittest.TestCase):

    def test_init(self):

        a = rangeset.RangeSet()

        self.assertIsInstance(a, list)
        self.assertEqual(0, len(a))
        self.assertIs(int, a.element_type)

        a = rangeset.RangeSet([])

        self.assertEqual(0, len(a))

        a = rangeset.RangeSet([], element_type=float)
        self.assertIs(float, a.element_type)

    def test_invalid_element_type(self):

        cases = (
            int, long, float, str, tuple, list
        )

        dd()
        for typ in cases:
            dd('test valid type: ', typ)
            rangeset.Range(typ(), typ(), element_type=typ)
            rangeset.RangeSet([[typ(), typ()]], element_type=typ)

        cases = (
            lambda x: 1,
            True,
        )

        dd()
        for val in cases:
            dd('test invalid type: ', typ)
            self.assertRaises(TypeError, rangeset.Range, [], element_type=type(val))
            self.assertRaises(TypeError, rangeset.Range, [val, val])

            self.assertRaises(TypeError, rangeset.RangeSet, [], element_type=type(val))
            self.assertRaises(TypeError, rangeset.RangeSet, [[val, val]])

        # incompatible type
        self.assertRaises(TypeError, rangeset.Range, 1, 'a')

    def test_range_left_le_right(self):
        self.assertRaises(ValueError, rangeset.Range, 1, 0)

    def test_int_compare(self):

        a = rangeset.RangeSet([])

        self.assertEqual([], a)

    def test_range_incorrect_order(self):
        cases = (
            [[None, None], [1,    2]],
            [[0,    None], [1,    2]],
            [[1,    2],    [None, 5]],
            [[1,    2],    [2,    3]],
            [[1,    4],    [3,    5]],
            [[3,    4],    [1,    2]],
        )

        for rs in cases:
            dd('case:', rs)

            try:
                rangeset.RangeSet(rs)
            except Exception as e:
                dd(repr(e))
            self.assertRaises(ValueError, rangeset.RangeSet, rs)

    def test_range_cmp(self):

        cases = (
                ([None, None], [None, None], 0),
                ([None, 1], [1, None], 0),
                ([None, 1], [1, 2], 0),
                ([None, 1], [2, 3], -1),
                ([1, None], [None, 1], 0),
                ([1, None], [None, 0], 1),
                ([1, None], [-1, 0], 1),

                ([0, 1], [1, None], 0),
                ([0, 2], [1, None], 0),
                ([-1, 0], [1, None], -1),
        )

        for a, b, expected in cases:

            dd('case:', a, b, expected)

            a = rangeset.Range(*a)
            b = rangeset.Range(*b)

            rst = a.cmp(b)
            dd('rst:', rst)
            self.assertEqual(expected, rst)

    def test_int_add_error(self):

        cases = (
                ([], None, TypeError),
                ([], True, TypeError),
                ([], {}, TypeError),
                ([], 1, TypeError),
                ([], 1.1, TypeError),
                ([], [1, 2, 3], ValueError),
                ([], lambda x: True, TypeError),
        )

        dd()
        for init, ins, err in cases:
            dd('case: ', init, ins, err)

            a = rangeset.RangeSet(init, element_type=int)
            self.assertRaises(err, a.add, ins)

    def test_int_add(self):

        cases = (
            # add into empty range set.

                ([], [1, 1], [[1, 1]]),
                ([], [1, 2], [[1, 2]]),
                ([], [1, 3], [[1, 3]]),

            # collapse two range if necesary.

                ([[10, 20], [30, 40]], [1, 2],   [[1,  2],  [10, 20], [30, 40]]),
                ([[10, 20], [30, 40]], [1, 10],  [[1,  20], [30, 40]]),
                ([[10, 20], [30, 40]], [1, 12],  [[1,  20], [30, 40]]),
                ([[10, 20], [30, 40]], [10, 15], [[10, 20], [30, 40]]),
                ([[10, 20], [30, 40]], [11, 15], [[10, 20], [30, 40]]),
                ([[10, 20], [30, 40]], [1, 22],  [[1,  22], [30, 40]]),
                ([[10, 20], [30, 40]], [15, 25], [[10, 25], [30, 40]]),
                ([[10, 20], [30, 40]], [20, 25], [[10, 25], [30, 40]]),
                ([[10, 20], [30, 40]], [22, 25], [[10, 20], [22, 25], [30, 40]]),
                ([[10, 20], [30, 40]], [22, 30], [[10, 20], [22, 40]]),
                ([[10, 20], [30, 40]], [22, 32], [[10, 20], [22, 40]]),
                ([[10, 20], [30, 40]], [30, 32], [[10, 20], [30, 40]]),
                ([[10, 20], [30, 40]], [30, 42], [[10, 20], [30, 42]]),
                ([[10, 20], [30, 40]], [32, 42], [[10, 20], [30, 42]]),
                ([[10, 20], [30, 40]], [40, 50], [[10, 20], [30, 50]]),
                ([[10, 20], [30, 40]], [42, 50], [[10, 20], [30, 40], [42, 50]]),

            # overlapping with more than one range

                ([[10, 20], [30, 40]], [20, 30], [[10, 40]]),
                ([[10, 20], [30, 40]], [19, 30], [[10, 40]]),
                ([[10, 20], [30, 40]], [20, 31], [[10, 40]]),
                ([[10, 20], [30, 40]], [0, 35],  [[0, 40]]),
                ([[10, 20], [30, 40]], [15, 50], [[10, 50]]),
                ([[10, 20], [30, 40]], [15, 50], [[10, 50]]),

                ([[10, 20], [30, 40]], [15, None], [[10, None]]),
                ([[10, 20], [30, 40]], [None, 15], [[None, 20], [30, 40]]),
                ([[10, 20], [30, 40]], [None, 35], [[None, 40]]),
                ([[10, 20], [30, 40]], [None, None], [[None, None]]),

        )

        dd()
        for init, ins, expected in cases:

            dd('cases: ', init, ins, expected)

            a = rangeset.RangeSet(init, element_type=int)

            a.add(ins)

            self.assertEqual(expected, a)

    def test_rangeset_has(self):

        rs = rangeset.RangeSet([[None, 1], [10, 20], [30, 40], [50, None]])
        cases = (
            (-1, True),
            (0, True),
            (1, False),
            (5, False),
            (9, False),
            (10, True),
            (15, True),
            (20, False),
            (21, False),
            (29, False),
            (30, True),
            (31, True),
            (40, False),
            (49, False),
            (50, True),
            (51, True),
        )

        for val, expected in cases:
            dd('case:', val, expected)

            rst = rs.has(val)
            dd('rst:', rst)

            self.assertEqual(expected, rst)
