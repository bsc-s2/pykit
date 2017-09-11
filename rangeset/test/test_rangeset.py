import logging
import unittest

from pykit import rangeset
from pykit import ututil

dd = ututil.dd

logger = logging.getLogger(__name__)


class TestRange(unittest.TestCase):

    def test_init(self):
        a = rangeset.Range(1, 2)
        dd(a)
        a = rangeset.Range(1, 1)
        dd(a)

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

    def test_is_adjacent(self):
        cases = (
                ([None, None], [None, None], False),
                ([None, 0],    [0,    None], True),
                ([None, 1],    [1,    None], True),
                ([None, 1],    [2,    None], False),
                ([None, 1],    [None, 2],    False),
                ([1,    None], [1,    None], False),
                ([0,    1],    [1,    3],    True),
                ([1,    1],    [1,    1],    True),
                ([0,    1],    [2,    3],    False),
        )

        for a, b, expected in cases:
            dd('case:', a, b, expected)

            a = rangeset.Range(*a)
            b = rangeset.Range(*b)

            rst = a.is_adjacent(b)
            dd('rst:', rst)

            self.assertEqual(expected, rst)

    def test_cmp(self):

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

    def test_substract(self):
        cases = (
            ([None, None], [None, None], [None,      None]),
            ([None, None], [1,    None], [[None, 1], None]),
            ([None, None], [None, 1],    [None,      [1, None]]),
            ([None, None], [1,    3],    [[None, 1], [3, None]]),
            ([None, 5],    [5,    8],    [[None, 5], None]),
            ([None, 5],    [4,    8],    [[None, 4], None]),
            ([None, 5],    [1,    2],    [[None, 1], [2, 5]]),
            ([None, 5],    [None, 2],    [None,      [2, 5]]),
            ([None, 5],    [None, 5],    [None,      None]),
            ([5,    None], [1,    2],    [None,      [5, None]]),
            ([5,    None], [1,    8],    [None,      [8, None]]),
            ([5,    None], [5,    8],    [None,      [8, None]]),
            ([5,    None], [6,    8],    [[5, 6],    [8, None]]),
            ([5,    None], [6,    None], [[5, 6],    None]),
            ([5,    None], [5,    None], [None,      None]),
            ([5,    None], [4,    None], [None,      None]),
            ([5,    10],   [5,    None], [None,      None]),
            ([5,    10],   [6,    None], [[5, 6],    None]),
            ([5,    10],   [6,    7],    [[5, 6],    [7, 10]]),
            ([5,    10],   [6,    10],   [[5, 6],    None]),
        )

        for a, b, expected in cases:
            dd('case:', a, b, expected)

            a = rangeset.Range(*a)
            b = rangeset.Range(*b)

            rst = rangeset.substract_range(a, b)
            dd('rst:', rst)

            self.assertEqual(expected, rst)

    def test_length(self):
        inf = float('inf')
        cases = (
            ([None, None], inf),
            ([1, None], inf),
            ([None, 1], inf),
            ([None, ''], inf),
            ([None, ()], inf),
            ([None, []], inf),

            ([1, 2], 1),
            ([1.0, 2.2], 1.2),
        )

        for rng, expected in cases:
            dd('case:', rng, expected)

            rst = rangeset.Range(*rng).length()
            dd('rst:', rst)

            self.assertAlmostEqual(expected, rst)

        self.assertRaises(TypeError, rangeset.Range('', 'a').length)


class TestRangeSet(unittest.TestCase):

    def test_init(self):

        a = rangeset.RangeSet()

        self.assertIsInstance(a, list)
        self.assertEqual(0, len(a))

        a = rangeset.RangeSet([])

        self.assertEqual(0, len(a))

    def test_invalid_element_type(self):

        cases = (
            int, long, float, str, tuple, list
        )

        dd()
        for typ in cases:
            dd('test valid type: ', typ)
            rangeset.Range(typ(), typ())
            rangeset.RangeSet([[typ(), typ()]])

        cases = (
            lambda x: 1,
            True,
        )

        dd()
        for val in cases:
            dd('test invalid type: ', typ)
            self.assertRaises(TypeError, rangeset.Range, [val, val])

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

            a = rangeset.RangeSet(init)
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

            a = rangeset.RangeSet(init)

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

    def test_union(self):

        cases = (
            ([[None, 10], [20, 30], [40, None]], [[None, None]],  [[None, None]]),

            ([[None, 10], [20, 30], [40, None]], [[None, 1]],  [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[None, 10]], [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[None, 11]], [[None, 11],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[9,    11]], [[None, 11],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[10,   11]], [[None, 11],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[11,   12]], [[None, 10], [11, 12], [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[19,   20]], [[None, 10],           [19, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[19,   21]], [[None, 10],           [19, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[20,   21]], [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[24,   25]], [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[29,   30]], [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[29,   31]], [[None, 10],           [20, 31],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[30,   31]], [[None, 10],           [20, 31],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[31,   32]], [[None, 10],           [20, 30], [31, 32], [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[39,   40]], [[None, 10],           [20, 30],           [39, None]]),
            ([[None, 10], [20, 30], [40, None]], [[39,   41]], [[None, 10],           [20, 30],           [39, None]]),
            ([[None, 10], [20, 30], [40, None]], [[40,   41]], [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[41,   42]], [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[41,   None]], [[None, 10],           [20, 30],           [40, None]]),

            ([[None, 10], [20, 30], [40, None]], [[8, 25], [35, 40]], [[None, 30], [35, None]]),
        )

        dd()
        for a, b, expected in cases:
            dd('case:', a, b, expected)

            a = rangeset.RangeSet(a)
            b = rangeset.RangeSet(b)

            rst = rangeset.union(a, b)

            dd('rst:', rst)

            self.assertEqual(expected, rst)

    def test_substract(self):

        cases = (
            ([[None, 10], [20, 30], [40, None]], [[None, None]],  []),

            ([[None, 10], [20, 30], [40, None]], [[None, 1]],    [[1,    10], [20, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[None, 10]],   [[20,   30],                               [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[None, 11]],   [[20,   30],                               [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[9,    11]],   [[None,  9], [20, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[10,   11]],   [[None, 10], [20, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[11,   12]],   [[None, 10], [20, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[19,   20]],   [[None, 10], [20, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[19,   21]],   [[None, 10], [21, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[20,   21]],   [[None, 10], [21, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[24,   25]],   [[None, 10], [20, 24], [25, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[29,   30]],   [[None, 10], [20, 29],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[29,   31]],   [[None, 10], [20, 29],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[30,   31]],   [[None, 10], [20, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[31,   32]],   [[None, 10], [20, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[39,   40]],   [[None, 10], [20, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[39,   41]],   [[None, 10], [20, 30],                     [41, None]]),
            ([[None, 10], [20, 30], [40, None]], [[40,   41]],   [[None, 10], [20, 30],                     [41, None]]),
            ([[None, 10], [20, 30], [40, None]], [[41,   42]],   [[None, 10], [20, 30],           [40, 41], [42, None]]),
            ([[None, 10], [20, 30], [40, None]], [[41,   None]], [[None, 10], [20, 30],           [40, 41], ]),

            ([[20, 30]], [[20, 24], [25, 30]], [[24, 25]]),
            ([[None, 10], [20, 30], [40, None]], [[20, 24], [25, 30]], [[None, 10], [24, 25], [40, None], ]),
            ([[None, 10], [20, 30], [40, None]], [[1, 2], [8, 25], [35, 45]], [[None, 1], [2, 8], [25, 30], [45, None]]),
        )

        dd()
        for a, b, expected in cases:
            dd('case:', a, b, expected)

            a = rangeset.RangeSet(a)
            b = rangeset.RangeSet(b)

            rst = rangeset.substract(a, b)

            dd('rst:', rst)

            self.assertEqual(expected, rst)

    def test_intersect(self):

        cases = (
            ([[None, 10], [20, 30], [40, None]], [[None, None]],  [[None, 10], [20, 30], [40, None]]),

            ([[None, 10], [20, 30], [40, None]], [[None, 1]],    [[None, 1]]),
            ([[None, 10], [20, 30], [40, None]], [[None, 10]],   [[None, 10]]),
            ([[None, 10], [20, 30], [40, None]], [[None, 11]],   [[None, 10]]),
            ([[None, 10], [20, 30], [40, None]], [[9,    11]],   [[9, 10]]),
            ([[None, 10], [20, 30], [40, None]], [[10,   11]],   []),
            ([[None, 10], [20, 30], [40, None]], [[11,   12]],   []),
            ([[None, 10], [20, 30], [40, None]], [[19,   20]],   []),
            ([[None, 10], [20, 30], [40, None]], [[19,   21]],   [[20, 21]]),
            ([[None, 10], [20, 30], [40, None]], [[20,   21]],   [[20, 21]]),
            ([[None, 10], [20, 30], [40, None]], [[24,   25]],   [[24, 25]]),
            ([[None, 10], [20, 30], [40, None]], [[29,   30]],   [[29, 30]]),
            ([[None, 10], [20, 30], [40, None]], [[29,   31]],   [[29, 30]]),
            ([[None, 10], [20, 30], [40, None]], [[30,   31]],   []),
            ([[None, 10], [20, 30], [40, None]], [[31,   32]],   []),
            ([[None, 10], [20, 30], [40, None]], [[39,   40]],   []),
            ([[None, 10], [20, 30], [40, None]], [[39,   41]],   [[40, 41]]),
            ([[None, 10], [20, 30], [40, None]], [[40,   41]],   [[40, 41]]),
            ([[None, 10], [20, 30], [40, None]], [[41,   42]],   [[41, 42]]),
            ([[None, 10], [20, 30], [40, None]], [[41,   None]], [[41, None]]),

            ([[None, 10], [20, 30], [40, None]], [[1, 2], [8, 25], [35, 45]], [[1, 2], [8, 10], [20, 25], [40, 45]]),
        )

        dd()
        for a, b, expected in cases:
            dd('case:', a, b, expected)

            a = rangeset.RangeSet(a)
            b = rangeset.RangeSet(b)

            rst = rangeset.intersect(a, b)

            dd('rst:', rst)

            self.assertEqual(expected, rst)

    def test_length(self):
        rst = rangeset.RangeSet([[1, 2], [5, 8]]).length()
        self.assertEqual(4, rst)

        self.assertRaises(TypeError, rangeset.RangeSet([['', 'a']]).length)


class TestIntIncRangeSet(unittest.TestCase):

    def test_int_inc_substract(self):

        cases = (
            ([[None, 10], [20, 30], [40, None]], [[None, None]],  []),

            ([[None, 10], [20, 30], [40, None]], [[None, 1]],    [[2,    10], [20, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[None, 10]],   [[20,   30],                               [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[None, 11]],   [[20,   30],                               [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[9,    11]],   [[None,  8], [20, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[10,   11]],   [[None,  9], [20, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[11,   12]],   [[None, 10], [20, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[19,   20]],   [[None, 10], [21, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[19,   21]],   [[None, 10], [22, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[20,   21]],   [[None, 10], [22, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[24,   25]],   [[None, 10], [20, 23], [26, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[29,   30]],   [[None, 10], [20, 28],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[29,   31]],   [[None, 10], [20, 28],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[30,   31]],   [[None, 10], [20, 29],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[31,   32]],   [[None, 10], [20, 30],                     [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[39,   40]],   [[None, 10], [20, 30],                     [41, None]]),
            ([[None, 10], [20, 30], [40, None]], [[39,   41]],   [[None, 10], [20, 30],                     [42, None]]),
            ([[None, 10], [20, 30], [40, None]], [[40,   41]],   [[None, 10], [20, 30],                     [42, None]]),
            ([[None, 10], [20, 30], [40, None]], [[41,   42]],   [[None, 10], [20, 30],           [40, 40], [43, None]]),
            ([[None, 10], [20, 30], [40, None]], [[41,   None]], [[None, 10], [20, 30],           [40, 40], ]),

            ([[20, 30]], [[20, 23], [25, 30]], [[24, 24]]),
            ([[20, 30]], [[20, 22], [27, 30]], [[23, 26]]),
            ([[None, 10], [20, 30], [40, None]], [[20, 23], [26, 30]], [[None, 10], [24, 25], [40, None], ]),
            ([[None, 10], [20, 30], [40, None]], [[1, 2], [8, 25], [35, 45]], [[None, 0], [3, 7], [26, 30], [46, None]]),
        )

        dd()
        for a, b, expected in cases:
            dd('case:', a, b, expected)

            a = rangeset.RangeSet(a, range_clz=rangeset.IntIncRange)
            b = rangeset.RangeSet(b, range_clz=rangeset.IntIncRange)

            rst = rangeset.substract(a, b)

            dd('rst:', rst)

            self.assertEqual(expected, rst)

    def test_int_inc_union(self):

        cases = (
            ([[None, 10], [20, 30], [40, None]], [[None, None]],  [[None, None]]),

            ([[None, 10], [20, 30], [40, None]], [[None, 1]],  [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[None, 10]], [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[None, 11]], [[None, 11],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[9,    11]], [[None, 11],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[10,   11]], [[None, 11],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[11,   12]], [[None, 12],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[12,   13]], [[None, 10], [12, 13], [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[18,   19]], [[None, 10],           [18, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[19,   21]], [[None, 10],           [19, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[20,   21]], [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[24,   25]], [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[29,   30]], [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[29,   31]], [[None, 10],           [20, 31],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[30,   31]], [[None, 10],           [20, 31],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[31,   32]], [[None, 10],           [20, 32],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[32,   33]], [[None, 10],           [20, 30], [32, 33], [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[39,   39]], [[None, 10],           [20, 30],           [39, None]]),
            ([[None, 10], [20, 30], [40, None]], [[39,   40]], [[None, 10],           [20, 30],           [39, None]]),
            ([[None, 10], [20, 30], [40, None]], [[39,   41]], [[None, 10],           [20, 30],           [39, None]]),
            ([[None, 10], [20, 30], [40, None]], [[40,   41]], [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[41,   42]], [[None, 10],           [20, 30],           [40, None]]),
            ([[None, 10], [20, 30], [40, None]], [[41, None]], [[None, 10],           [20, 30],           [40, None]]),

            ([[None, 10], [20, 30], [40, None]], [[8, 25], [35, 40]], [[None, 30], [35, None]]),
        )

        dd()
        for a, b, expected in cases:
            dd('case:', a, b, expected)

            a = rangeset.RangeSet(a, range_clz=rangeset.IntIncRange)
            b = rangeset.RangeSet(b, range_clz=rangeset.IntIncRange)

            rst = rangeset.union(a, b)

            dd('rst:', rst)

            self.assertEqual(expected, rst)

    def test_int_inc_length(self):

        rst = rangeset.IntIncRangeSet([[1, 2], [5, 8]]).length()
        self.assertEqual(6, rst)

    def test_inherit_range_clz(self):

        a = rangeset.IntIncRangeSet([[1, 2]])
        b = rangeset.IntIncRangeSet([[2, 3], [5, 6]])

        cases = (
            rangeset.union,
            rangeset.substract,
            rangeset.intersect,
        )

        dd()

        for func in cases:
            dd('func:', func)

            rst = func(a, b)
            self.assertIs(a[0].__class__, rst[0].__class__)
            rst = func(b, a)
            self.assertIs(a[0].__class__, rst[0].__class__)

