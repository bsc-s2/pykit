#!/usr/bin/env python
# coding: utf-8

import unittest

from pykit import ututil
from pykit.mathtoy import Matrix
from pykit.mathtoy import Polynomial
from pykit.mathtoy import Vector

dd = ututil.dd


class TestVector(unittest.TestCase):

    def test_vector(self):

        a = Vector([1, 2, 3])
        b = a + [2, 3, 4]
        self.assertEqual([3, 5, 7], b)
        self.assertEqual([1, 2, 3], a)

        c = b - a
        self.assertEqual([2, 3, 4], c)
        b -= a
        self.assertEqual([2, 3, 4], b)

        d = a.inner_product([2, 3, 4])
        self.assertEqual(20, d)

    def test_vector_val(self):
        a = Vector([1, 2, 3])
        self.assertEqual([2, 4, 6], a * 2)

        self.assertEqual([1, 4, 9], a**2)


class TestMatrix(unittest.TestCase):

    def test_minor(self):
        a = Matrix([[1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9],
                    ])

        self.assertEqual([[5, 6],
                          [8, 9], ],
                         a.minor(0, 0))

        self.assertEqual([[1, 2],
                          [4, 5], ],
                         a.minor(2, 2))

    def test_determinant(self):

        a = Matrix([[2], ])
        self.assertEqual(2, a.determinant())

        a = Matrix([[1, 2],
                    [4, 5],
                    ])

        self.assertEqual(-3, a.determinant())

        a = Matrix([[-2, 2, -3],
                    [-1, 1, 3],
                    [2, 0, 1],
                    ])

        self.assertEqual(18, a.determinant())

    def test_replace(self):

        a = Matrix([[1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9],
                    ])

        a.replace_row(0, [0, 0, 0])
        self.assertEqual([[0, 0, 0],
                          [4, 5, 6],
                          [7, 8, 9]
                          ], a)

        a.replace_col(1, [8, 8, 8])
        self.assertEqual([[0, 8, 0],
                          [4, 8, 6],
                          [7, 8, 9]
                          ], a)

    def test_solve(self):

        cases = (
            ([[3, 5],
              [1, 2]],
             [4, 1],
             [3, -1]),
        )

        for m, y, expected in cases:
            m = Matrix(m)
            y = Vector(y)
            x = m.solve(y)
            self.assertEqual(expected, x)


class TestPolynomial(unittest.TestCase):
    def test_partial_derivative(self):
        xs = [1, 2, 3, 4]
        ys = [6, 5, 7, 10]

        m, yys = Polynomial.get_fitting_equation(xs, ys, degree=1)
        self.assertEqual([[8, 20],
                          [20, 60], ], m)
        self.assertEqual([56, 154], yys)

    def test_fit(self):
        xs = [1, 2, 3, 4]
        ys = [6, 5, 7, 10]

        coef = Polynomial.fit(xs, ys, degree=1)
        self.assertEqual([3.5, 1.4], coef)

        coef = Polynomial.fit(xs, ys, degree=2)
        self.assertEqual([8.5, -3.6, 1], coef)

    def test_plot(self):
        # TODO this is a sample

        print

        xs = [1, 2, 3, 4]
        ys = [6, 5, 7, 10]

        for deg in (0, 1, 2, 3):
            poly = Polynomial.fit(xs, ys, degree=deg)
            print 'y =', poly
            y5 = Polynomial.evaluate(poly, 5)
            print 'y(5) =', y5

            p1 = Polynomial.fit(xs, ys, degree=1)
            for l in Polynomial.plot([(p1, '.'), (poly, 'o'), ],
                                     (0, 6),
                                     width=60, height=12, points=zip(xs + [5], ys + [y5], ['X', 'X', 'X', 'X', '*'])):
                print l
