import random
import unittest

from pykit import heap
from pykit import ututil

dd = ututil.dd


class X(object):

    def __init__(self, val):
        self.x = val

    def __lt__(self, b):
        return self.x < b.x

    def __str__(self):
        return str(self.x)


class TestRefHeap(unittest.TestCase):

    def test_index_level(self):
        cases = (
                (1, 0),
                (2, 1),
                (3, 1),
                (4, 2),
                (5, 2),
                (6, 2),
                (7, 2),
        )

        for inp, expected in cases:
            dd('inp:', inp)
            rst = heap.index_level(inp)

            dd('rst:', rst)
            self.assertEqual(expected, rst)

    def test_push_pop_get(self):

        cases = (
                ([], 0),
                ([None, 3, 1, None], 0),
                ([1, 1, 2], 0),
                (['a'], 0),
                (['a', 'c', 'b'], 0),
                ('accbbdb', 0),
                ([5, 3, 7, 6, 8, 1], 0),
                ([6, 4, 1, 7, 8, 3, 2], 0),
        )

        for inp, _ in cases:

            dd('inp:', inp)
            h = heap.RefHeap(inp)
            dd('after push')
            dd(str(h))

            self.assertEqual(len(inp), h.size)

            rst = []
            for i, _ in enumerate(inp):

                val = h.get()
                self.assertEqual(sorted(inp)[i], val)
                self.assertEqual(len(inp) - i, h.size)

                val = h.pop()
                self.assertEqual(sorted(inp)[i], val)
                self.assertEqual(len(inp) - i - 1, h.size)

                rst.append(val)

            dd('after pop all')
            dd(str(h))
            dd('rst:', rst)

            self.assertEqual(0, h.size)

    def test_class_with_lt(self):

        case = (6, 4, 1, 7, 8, 3, 2)
        arr = [X(x) for x in case]

        h = heap.RefHeap(arr)
        dd('after push:')
        dd(str(h))

        rst = h.pop_all(map=lambda x: x.x)
        self.assertEqual(sorted(case), rst)

    def test_sift_naive(self):

        a, b = [1], [2]
        h = heap.RefHeap([a, b])

        self.assertIs(a, h.get())

        a[0] = 3
        h.sift(a)
        self.assertIs(b, h.get())

        b[0] = 5
        h.sift(b)
        self.assertIs(a, h.get())

        self.assertRaises(heap.NotFound, h.sift, [])

    def test_sift(self):

        case = [6, 4, 1, 7, 8, 3, 2]

        for i in range(len(case)):
            for repl in (0, 5, 10):

                arr = [X(x) for x in case]
                dd('case:', case)

                h = heap.RefHeap(arr)
                dd('init heap:')
                dd(str(h))

                dd('replace {i}-th item {v} to {repl}'.format(i=i, v=case[i], repl=repl))

                arr[i].x = repl
                h.sift(arr[i])

                dd('after sift:')
                dd(str(h))

                rst = h.pop_all(map=lambda x: x.x)

                expected = case[:]
                expected[i] = repl
                expected.sort()

                self.assertEqual(expected, rst)

    def test_remove(self):

        case = [6, 4, 1, 7, 8, 3, 2]

        for i in range(len(case)):

            arr = [X(x) for x in case]
            dd('case:', case)

            h = heap.RefHeap(arr)
            dd('init heap:')
            dd(str(h))

            dd('remove {i}-th item {v}'.format(i=i, v=case[i]))

            h.remove(arr[i])

            dd('after remove:')
            dd(str(h))

            rst = h.pop_all(map=lambda x: x.x)

            expected = case[:i] + case[i + 1:]
            expected.sort()

            self.assertEqual(expected, rst)

    def test_remove_not_found(self):

        h = heap.RefHeap()
        self.assertRaises(heap.NotFound, h.remove, X(0))

        a = X(1)
        h.push(a)
        h.remove(a)

        self.assertRaises(heap.NotFound, h.remove, a)
        self.assertRaises(heap.NotFound, h.remove, X(0))

    def test_pop_all(self):

        case = [6, 4, 1, 7, 8, 3, 2]
        dd('case:', case)
        h = heap.RefHeap(case)
        self.assertEqual(sorted(case), h.pop_all())
        self.assertEqual(0, h.size)

        h = heap.RefHeap([X(x) for x in case])
        self.assertEqual(sorted(case), h.pop_all(map=lambda x: x.x))
        self.assertEqual(0, h.size)

    def test_dup(self):
        x = X(1)
        h = heap.RefHeap([x])

        self.assertRaises(heap.Duplicate, h.push, x)

        h.push(X(1))
        dd(str(h))

        self.assertEqual(1, h.pop().x)
        self.assertEqual(1, h.pop().x)

    def test_dup_all_type(self):

        for inp in [[1], {1: 2}, set([3])]:

            h = heap.RefHeap()
            h.push(inp)
            self.assertRaises(heap.Duplicate, h.push, inp)

    def test_pop_from_empty(self):
        h = heap.RefHeap()

        self.assertRaises(heap.Empty, h.pop)
        self.assertRaises(heap.Empty, h.get)

        h.push(1)
        h.pop()
        self.assertRaises(heap.Empty, h.pop)
        self.assertRaises(heap.Empty, h.get)

        self.assertIsNone(h.root)

    def test_rand(self):
        n = 500
        case = [random.randint(0, n) for x in range(n * 2)]
        h = heap.RefHeap(case)
        rst = []
        for x in range(len(case)):
            rst.append(h.pop())

        self.assertEqual(sorted(case), rst)
