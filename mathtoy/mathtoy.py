#!/usr/bin/env python
# coding: utf-8


class Vector(list):

    def __init__(self, *args, **kwargs):
        super(Vector, self).__init__(*args, **kwargs)
        for i in range(len(self)):
            self[i] = float(self[i])

    def __add__(self, b):
        return Vector([self[i] + b[i] for i in range(len(self))])

    def __sub__(self, b):
        return Vector([self[i] - b[i] for i in range(len(self))])

    def __mul__(self, v):
        return Vector([self[i] * v for i in range(len(self))])

    def __pow__(self, v):
        return Vector([self[i] ** v for i in range(len(self))])

    def inner_product(self, b):
        return sum([self[i] * b[i] for i in range(len(self))])


class Matrix(list):

    def __init__(self, vectors):
        vectors = [Vector(x) for x in vectors]
        super(Matrix, self).__init__(vectors)

    def minor(self, i, j):
        vectors = [Vector(x) for x in self[:i]]
        vectors += [Vector(x) for x in self[i + 1:]]
        for v in vectors:
            v.pop(j)

        return Matrix(vectors)

    def determinant(self):
        if len(self) == 1:
            return self[0][0]

        if len(self) == 2:
            return self[0][0] * self[1][1] - self[0][1] * self[1][0]

        rst = 0
        for i in range(len(self)):
            rst += (-1) ** i * self[0][i] * self.minor(0, i).determinant()
        return rst

    def replace_row(self, i, vec):
        self[i] = Vector(vec)

    def replace_col(self, j, vec):
        for i in range(len(self)):
            self[i][j] = vec[i]

    def solve(self, ys):
        # Sovle linear equation M x [x] = [y]
        # with Cramer's rule
        xs = []
        det = self.determinant()
        for i in range(len(self)):
            m = Matrix(self)
            m.replace_col(i, ys)
            x = m.determinant() / det
            xs.append(x)

        return Vector(xs)

    def invert(self):
        # TODO test
        rst = []
        for i in range(len(self)):
            vi = []
            for j in range(len(self)):
                vi.append(self.minor(j, i).determinant())

            vi = Vector(vi)
            vi = vi * (1.0 / self.determinant())

            rst.append(vi)

        return Matrix(rst)


class Polynomial(list):
    """
    xs and ys is array of x-coordinate value and y-coordinate value.
    They are all real numbers.

    xs = [1, 2, 3, 4, 5..]
    ys = [1, 2, 4, 7, 11..]

    With xs and ys to calc the coefficients of a polinomial

    degree is the highest power of polinomial:
    degree=2: y = a0 + a1*x + a2*x^2

    """

    def __str__(self):
        # TODO test
        super_num = u'⁰¹²³⁴⁵⁶⁷⁸⁹'

        rst = []
        for i, coef in enumerate(self):
            if coef == 0:
                continue

            if coef == 1:
                c = ''
            elif int(coef) == coef:
                c = str(int(coef))
            else:
                c1 = '{:>4f}'.format(coef)
                c1 = c1.rstrip('0')
                c2 = '{:>4e}'.format(coef)
                if len(c1) > len(c2):
                    c = c2
                else:
                    c = c1

            if i == 0:
                rst.append(c)
            elif i == 1:
                rst.append(c + 'x')
            else:
                pw = str(i)
                pw = ''.join([super_num[int(x)] for x in pw])
                rst.append(c + 'x' + pw.encode('utf-8'))

        rst = ' + '.join(rst)
        return rst.replace(' + -', ' - ')

    @classmethod
    def get_fitting_equation(clz, xs, ys, degree):
        # TODO test
        """
        Curve fit with least squres

        We looking for a curve:

            Y = a0 + a1*x + a2*x^2

        that minimize variance:

            E = sum((Y[i]-ys[i])^2)

        Partial derivatives about a0..an are:

            E'a0 = sum(2 * (a0 + a1*xs[i] + a2*xs[i]^2 - ys[i]) * 1)
            E'a1 = sum(2 * (a0 + a1*xs[i] + a2*xs[i]^2 - ys[i]) * xs[i])
            E'a2 = sum(2 * (a0 + a1*xs[i] + a2*xs[i]^2 - ys[i]) * xs[i]^2)

        The best fit is a curve that minimizes E:
        or all partial derivatives are 0:

            | c00 c01 c02 |   | a0 |   | Y0 |
            | c10 c11 c12 | * | a1 | = | Y1 |
            | c20 c21 c22 |   | a2 |   | Y2 |

            c00 = 2 * n
            c01 = 2 * sum(xs[i])
            c02 = 2 * sum(xs[i]^2)
            Y0  = 2 * sum(ys[i])

            c10 = 2 * sum(xs[i])
            c11 = 2 * sum(xs[i]^2)
            c12 = 2 * sum(xs[i]^3)
            Y1  = 2 * sum(ys[i]*xs[i])

            ...

        """

        xs, ys = Vector(xs), Vector(ys)
        coef = []

        yys = Vector()

        for deg in range(0, degree + 1):
            # o[i] is coefficient of a[i] of E'a[i]
            o = Vector([0] * (degree + 1))
            y = 0
            for i in range(len(xs)):
                # a0 + a1*xs[i] + a2*xs[i]^2
                v = Vector([0] * (degree + 1))
                for ai in range(degree + 1):
                    v[ai] = xs[i] ** ai
                v = v * 2
                v = v * (xs[i] ** deg)
                o = o + v

                y += ys[i] * 2 * xs[i] ** deg

            coef.append(o)
            yys.append(y)

        coef = Matrix(coef)

        return coef, yys

    @classmethod
    def fit(clz, xs, ys, degree):
        xs, ys = Vector(xs), Vector(ys)

        m, yys = clz.get_fitting_equation(xs, ys, degree)

        coef = m.solve(yys)

        return clz(coef)

        # return coef

    @classmethod
    def evaluate(clz, coefficients, x):
        # TODO test
        r = 0
        for i, ee in enumerate(coefficients):
            r += ee * (x**i)
        return r

    @classmethod
    def variance(clz, coefficients, xs, ys):
        # TODO test
        yys = [clz.evaluate(coefficients, x) for x in xs]
        pairs = zip(yys, ys)
        sm = sum([(a - b)**2 for a, b in pairs]) / len(xs)
        return sm

    @classmethod
    def interpolation(clz, xs, ys, degree, x):
        # TODO test
        """
        guess value at x with polynomial regression
        """

        # curve fit
        coef = clz.fit(xs, ys, degree)
        return clz.evaluate(coef, x)

    @classmethod
    def plot(clz, polynomials, rangex, rangey=None, width=120, height=20, points=()):
        # polynomials: is list of coefficients and point symbol
        #
        # [
        #     ([0, 1, 2], '.'),
        #     ([0, 2], 'x'),
        # ]
        # TODO test
        rangex = (float(rangex[0]), float(rangex[1]))
        rng_width = rangex[1] - rangex[0]
        ys = []
        jys = []
        for i in range(width):
            x = float(i) / width * rng_width + rangex[0]
            for poly, sym in polynomials:
                y = clz.evaluate(poly, x)
                ys.append(y)
                jys.append((i, y, sym))

        if rangey is None:
            y_range = ys + [xx[1] for xx in points]
        else:
            y_range = [rangey[0], rangey[1]]

        bot, top = min(y_range), max(y_range)

        lines = []
        for ii in range(height + 1):
            lines.append([' '] * (width + 1))

        for j, y, sym in jys:
            h = y - bot
            h = h * height / (top - bot)
            h = int(h)

            if height - h < 0:
                continue
            try:
                lines[height - h][j] = sym
            except IndexError:
                # point out of range. ignore
                pass

        for ii, xyv in enumerate(points):
            x, y = xyv[:2]
            if len(xyv) > 2:
                v = str(xyv[2])
            else:
                v = 'X'
            h = y - bot
            i = h * height / (top - bot)
            i = int(i)
            i = height - i

            j = (float(x) - rangex[0]) * width / rng_width
            j = int(j)

            if 0 <= i <= height and 0 <= j <= width:
                txt = v
                m = j
                while m <= width and m - j < len(txt):
                    lines[i][m] = txt[m - j]
                    m += 1

        lines = [''.join(xx) for xx in lines]
        return lines
