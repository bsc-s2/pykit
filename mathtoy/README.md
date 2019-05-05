<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Synopsis](#synopsis)
- [Classes](#classes)
  - [Vector](#vector)
    - [Vector.inner_product](#vectorinner_product)
  - [Matrix](#matrix)
    - [Matrix.minor](#matrixminor)
    - [Matrix.determinant](#matrixdeterminant)
    - [Matrix.solve](#matrixsolve)
  - [Polynomial](#polynomial)
    - [Polynomial.fit](#polynomialfit)
    - [Polynomial.plot](#polynomialplot)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

mathtoy

#   Status

This library is a experiment math utility set.

It is not ready for production use, but for education and demonstration.

The correctness is proved but the performance is probably very poor.

#   Description

#   Synopsis

```python
xs = [1, 2, 3, 4]
ys = [6, 5, 7, 10]

# Fit polynomial curve with 4 points, at degree 0, 1, 2, 3:
for deg in (0, 1, 2, 3):
    poly = Polynomial.fit(xs, ys, degree=deg)
    print 'y =', poly

    # Evaluate y(5) with polynomial
    y5 = Polynomial.evaluate(poly, 5)
    print 'y(5) =', y5

    # Plot the curve and points
    lines = Polynomial.plot([(poly, '.')], (-1, 6),
                            width=30, height=10,
                            points=zip(xs + [5],
                                       ys + [y5],
                                       ['X', 'X', 'X', 'X', '*']))
    for l in lines:
        print l

# y = 7
# y(5) = 7.0
#                     X
#
#
#
# ...............X.........*....
#      X
#           X
# y = 3.5 + 1.4x
# y(5) = 10.5
#                              .
#                          *...
#                     X....
#                .....
#           .....X
#      X....X
# .....
# y = 8.5 - 3.6x + x²
# y(5) = 15.5
#                              .
#                             .
#                           ..
#                         .*
#                      ...
# ..               ...X
#   ...X....X....X.
# y = 12 - 9.166667x + 3.5x² - 0.333333x³
# y(5) = 12.0
#
# .                     ...*....
#  .                  X.
#   .               ..
#    .            ..
#     .         .X
#      X....X...
```

#   Classes

##  Vector

**syntax**:
`Vector(list)`

A `Vector` is a `list` supporting operations:

-   `+`: vector adds vector
-   `-`: vector subtracts vector
-   `*`: vector times scalar
-   `**`: vector powers scalar

###  Vector.inner_product

**syntax**:
`Vector.inner_product(b)`

Calculate inner product of two vector.

**arguments**:

-   `b`: another Vector

**return**:
a new Vector


##  Matrix

**syntax**:
`Matrix(vectors)`


###  Matrix.minor

**syntax**:
`Matrix.minor(i, j)`

Make a new matrix without i-th row and j-th column.

**arguments**:

-   `i` and `j`: row index and column index.

**return**:
a new Matrix


###  Matrix.determinant

**syntax**:
`Matrix.determinant()`

Calculate determinant of a matrix. E.g.:

```
| a b | = a*d - b*c
| c d |
```

**return**:
a `float` value.


###  Matrix.solve

**syntax**:
`Matrix.solve(y)`

Solve equations:

```
|a00 a01 a02|   |x0|   |y0|
|a10 a11 a12| * |x1| = |y1|
|a20 a21 a22|   |x2|   |y2|
```

**arguments**:

-   `y`: a vector of `y0, y1, y2`.

**return**:
a vector of `|x|: x0, x1, x2`


##  Polynomial

**syntax**:
`Polynomial(coefficients)`

It represents a polynomial: `y = a0 + a1 * x^1 + a2 * x^2 ..`.
Where `coefficients = [a0, a1, a2 .. ]`.

**arguments**:

-   `coefficients`: is a vector of coefficients.


###  Polynomial.fit

**syntax**:
`Polynomial.fit(x, y, degree)`

Find a polynomial curve with least squares method.

**arguments**:

-   `x, y`: vector of x positions and y positions.

-   `degree`: the highest power of variable `x` in the polynomial.

**return**:
a `Polynomial` instance.


###  Polynomial.plot

**syntax**:
`Polynomial.plot(polynomials, rangex, rangey=None, width=120, height=20, points=())`

Plot a polynomial.

**Synopsis**:

```python
from pykit.mathtoy import Polynomial

# y = 3.5 + 3.4x + x^2
poly = [3.5, 3.4, 1]

for l in Polynomial.plot([(poly, '.')],
                         rangex=[-1, 6],
                         width=40, height=10):
    print l
#                                        .
#                                      ..
#                                    ..
#                                  ..
#                               ...
#                            ...
#                         ...
#                     ....
#                 ....
#            .....
# ...........
```

**arguments**:

-   `polynomials`: list of a vector of polynomial coefficients and symbol:

    ```python
    [ ([1, 6], 'x'),    # y = 1 + 6x, plot with "x"
      ([2, 2, 2], '.'), # y = 2 + 2x + 2x^2, plot with "."
    ]
    ```

-   `rangex`:
    is a tuple of two floats that specifies range of x.

-   `rangey`:
    is a tuple of two floats that specifies range of y.

-   `width`: specifies plot graph width.

-   `height`: specifies plot graph height.

-   `points`:
    other points to add to the plot.
    It is a vector of `(x, y[, char])`.
    `char` is optional to specify point mark.
    By default it is `X`.

**return**:
a list of strings.


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
