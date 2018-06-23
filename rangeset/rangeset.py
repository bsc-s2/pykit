

int_types = (int, long)
list_like = (type([]), type(()))

compatible_types = {
    type(None): (type(None), ),
    int:        (type(None), int, ),
    long:       (type(None), int,   long, ),
    float:      (type(None), int,   long, float, ),
    str:        (type(None), str,),
    tuple:      (type(None), tuple, ),
    list:       (type(None), list,),
}


class RangeException(Exception):
    pass


class Unmergeable(RangeException):
    pass


class ValueRange(list):

    def __init__(self, left, right, val=None):

        assert_compatible(left, right)

        if cmp_boundary(left, right) > 0:
            raise ValueError('left not smaller or equal right: {left}, {right}'.format(
                left=left, right=right))

        super(ValueRange, self).__init__([left, right, val])

    def cmp(self, b):

        # if a and b can be merged into one range, we say a == b
        #
        # Different from Range: adjacent ValueRange-s are not equal,
        # because they have their own value bound and can not be merged.

        if cmp_boundary(self[0], b[1]) >= 0:
            return 1

        if cmp_boundary(b[0], self[1]) >= 0:
            return -1

        # incomparable: overlapping or adjacent ranges
        return 0

    def intersect(self, b):

        if self.cmp(b) != 0:
            return None

        rst = [None, None] + self[2:]

        if self.cmp_left(b[0]) < 0:
            rst[0] = b[0]
        else:
            rst[0] = self[0]

        if self.cmp_right(b[1]) > 0:
            rst[1] = b[1]
        else:
            rst[1] = self[1]

        if rst[0] is not None and rst[0] == rst[1]:
            return None

        return rst

    def cmp_left(self, pos):
        # left is None means it is negative infinite
        return cmp_val(self[0], pos, none_cmp_finite=-1)

    def cmp_right(self, pos):
        # right is None means it is positive infinite
        return cmp_val(self[1], pos, none_cmp_finite=1)

    def is_adjacent(self, b):
        return cmp_boundary(b[0], self[1]) == 0

    def has(self, pos):
        return (self.cmp_left(pos) <= 0
                and self.cmp_right(pos) > 0)

    def length(self):
        if self[0] is None or self[1] is None:
            return float('inf')

        if isinstance(self[0], basestring):

            a, b = self[:2]
            l = max([len(a), len(b)])

            rst = 0.0
            ratio = 1.0
            for i in range(l):

                if i >= len(a):
                    va = 0.0
                else:
                    va = ord(a[i]) + 1.0

                if i >= len(b):
                    vb = 0.0
                else:
                    vb = ord(b[i]) + 1.0
                rst += (vb - va) / 257.0 * ratio
                ratio /= 257.0

            return rst
        else:
            return self[1] - self[0]

    def dup(self):
        return self.__class__(*self)

    def next_left(self):
        return self[1]

    def prev_right(self):
        return self[0]


class Range(ValueRange):

    def __init__(self, left, right):

        assert_compatible(left, right)

        if cmp_boundary(left, right) > 0:
            raise ValueError('left not smaller or equal right: {left}, {right}'.format(
                left=left, right=right))

        super(ValueRange, self).__init__([left, right])

    def cmp(self, b):

        # if a and b can be merged into one range, we say a == b
        #
        # Different from ValueRange: adjacent Range-s are equal,
        # because they can be merged into one.

        if cmp_boundary(self[0], b[1]) > 0:
            return 1

        if cmp_boundary(b[0], self[1]) > 0:
            return -1

        # incomparable: overlapping or adjacent ranges
        return 0


class IntIncRange(Range):

    def __init__(self, left, right):

        if left is not None and type(left) not in int_types:
            raise TypeError('{l} {ltyp} is not int or None'.format(
                l=left, ltyp=type(left)))

        if right is not None and type(right) not in int_types:
            raise TypeError('{r} {rtyp} is not int or None'.format(
                r=right, rtyp=type(right)))

        if cmp_boundary(left, right) > 0:
            raise ValueError('left not smaller or equal right: {left}, {right}'.format(
                left=left, right=right))

        list.__init__(self, [left, right])

    def cmp(self, b):

        # if a and b can be merged into one range, we say a == b

        if None not in (self[0], b[1]) and self[0] - b[1] > 1:
            return 1

        if None not in (b[0], self[1]) and b[0] - self[1] > 1:
            return -1

        # incomparable: overlapping or adjacent ranges
        return 0

    def is_adjacent(self, b):
        return (None not in (b[0], self[1])
                and self[1] + 1 == b[0])

    def has(self, pos):
        return (cmp_val(self[0], pos, none_cmp_finite=-1) <= 0
                and cmp_val(pos, self[1], none_cmp_finite=1) <= 0
                and type(pos) in int_types)

    def length(self):
        if None in self:
            return float('inf')

        return self[1] - self[0] + 1

    def next_left(self):
        return self[1] + 1

    def prev_right(self):
        return self[0] - 1


class RangeDict(list):

    default_range_clz = ValueRange

    def __init__(self, iterable=None, range_clz=None):

        if iterable is None:
            iterable = []

        self.range_clz = range_clz or self.default_range_clz

        super(RangeDict, self).__init__([self.range_clz(*x)
                                         for x in iterable])

        for i in range(0, len(self) - 1):
            if self[i].cmp(self[i + 1]) != -1:
                raise ValueError('range[{i}] {ri} does not smaller than range[{j}] {ripp}'.format(
                    i=i,
                    j=i + 1,
                    ri=self[i],
                    ripp=self[i + 1],
                ))

    def add(self, rng, val=None):

        rng = _to_range(self.range_clz, list(rng) + [val])

        i = bisect_left(self, rng)

        while i < len(self):

            if rng.cmp(self[i]) == 0:

                l, r = substract_range(self[i], rng)
                if l is None:
                    if r is None:
                        self.pop(i)
                    else:
                        self[i] = r
                        i += 1
                else:
                    if r is None:
                        self[i] = l
                        i += 1
                    else:
                        self.pop(i)
                        self.insert(i, r)
                        self.insert(i, l)
                        i += 2
            else:
                break

        if rng[0] is None:
            self.insert(0, rng)
        else:
            for i in range(len(self)):
                if self[i].cmp_left(rng[0]) > 0:
                    self.insert(i, rng)
                    break
            else:
                self.append(rng)

        self.normalize()

    def get(self, pos):
        rng = [pos, None]
        i = bisect_left(self, rng)

        if i == len(self) or not self[i].has(pos):
            raise KeyError('not in range: ' + repr(pos))

        return self[i][2]

    def has(self, pos):
        rng = [pos, None]
        i = bisect_left(self, rng)

        if i == len(self):
            return False

        return self[i].has(pos)

    def length(self):
        rst = 0
        for rng in self:
            rst += rng.length()

        return rst

    def normalize(self):

        i = 0
        while i < len(self) - 1:
            curr = self[i]
            nxt = self[i+1]

            if not curr.is_adjacent(nxt):
                i += 1
                continue

            # compare value if there is
            if curr[2:] == nxt[2:]:
                o = [curr[0], nxt[1]] + curr[2:]
                self[i] = self.range_clz(*o)
                self.pop(i+1)
            else:
                i += 1
                continue

    def find_overlapped(self, rng):

        rng = list(rng)
        rst = []

        i = bisect_left(self, rng)
        while i < len(self):

            if self[i].cmp(rng) == 0:

                if self[i].intersect(rng) is not None:
                    rst.append(self.range_clz(*self[i]))
                else:
                    # adjacent ranges
                    pass
                i += 1
            else:
                break

        return self.__class__(rst)


class RangeSet(RangeDict):

    default_range_clz = Range

    def add(self, rng):

        rng = _to_range(self.range_clz, list(rng))

        i = bisect_left(self, rng)

        while i < len(self):
            if rng.cmp(self[i]) == 0:
                rng = union_range(rng, self[i])
                self.pop(i)
            else:
                break

        self.insert(i, rng)


class IntIncRangeSet(RangeSet):
    default_range_clz = IntIncRange


def union(a, *bs):
    u = a
    for b in bs:
        u = _union(u, b)
    return u


def _union(a, b):

    if len(a) == 0:
        return RangeSet(b, range_clz=b.range_clz)

    if len(b) == 0:
        return RangeSet(a, range_clz=b.range_clz)

    rst = []
    i, j = 1, 0

    rng = a[0]

    while i < len(a) or j < len(b):

        a_ge_b = None

        if i == len(a):
            a_ge_b = True
        elif j == len(b):
            a_ge_b = False
        else:
            a_ge_b = a[i].cmp_left(b[j][0]) >= 0

        if a_ge_b:
            nxt = b[j]
            j += 1
        else:
            nxt = a[i]
            i += 1

        if rng.cmp(nxt) == 0:
            rng = union_range(rng, nxt)
        else:
            assert rng.cmp(nxt) < 0
            rst.append(rng)
            rng = nxt

    rst.append(rng)

    return RangeSet(rst, range_clz=b.range_clz)


def substract(a, *bs):
    s = a
    for b in bs:
        s = _substract(s, b)
    return s


def _substract(a, b):

    if len(a) == 0:
        return a.__class__([], range_clz=a.range_clz)

    if len(b) == 0:
        return a.__class__(a, range_clz=a.range_clz)

    rst = []

    for ra in a:

        sb = a.range_clz(*ra)

        j = bisect_left(b, ra)

        while j < len(b) and sb.cmp(b[j]) == 0:
            u1, u2 = substract_range(sb, b[j])

            if u1 is not None:
                rst.append(u1)

            sb = u2

            if sb is None:
                break

            j += 1

        if sb is not None:
            rst.append(sb)

    return a.__class__(rst, range_clz=a.range_clz)


def intersect(a, b):
    return substract(a, substract(a, b))


def assert_type_valid(typ):
    if typ not in compatible_types:
        raise TypeError('{typ} is not comparable'.format(typ=typ))


def _to_range(range_clz, rng):

    # rangeset is 2 element iterable, rangedict is 3 element iterable
    if len(rng) < 2:
        raise ValueError('range length is at least 2 but {l}: {rng}'.format(
            l=len(rng), rng=rng))

    return range_clz(*rng)


def cmp_boundary(l, r):

    if l is None:
        # left is -inf
        return -1

    if r is None:
        # right is inf
        return -1

    if l < r:
        return -1
    elif l > r:
        return 1
    else:
        return 0


def cmp_val(a, b, none_cmp_finite=1):

    # compare two value. any of them can be None.
    # None means positive infinite or negative infinite, defined by none_cmp_finite

    if a is None:
        if b is None:
            return 0
        else:
            # compare(none, b)
            return none_cmp_finite
    else:
        if b is None:
            # compare(b, none) = -compare(none, b)
            return -none_cmp_finite
        else:
            if a < b:
                return -1
            elif a > b:
                return 1
            else:
                return 0


def union_range(a, b):

    if a.cmp(b) != 0:
        raise Unmergeable(a, b)

    if a[0] is None or b[0] is None:
        left = None
    else:
        left = min([a[0], b[0]])

    if a[1] is None or b[1] is None:
        right = None
    else:
        right = max([a[1], b[1]])

    return a.__class__(left, right)


def substract_range(a, b):

    if a.cmp(b) > 0:
        # keep value for ValueRange
        return [None,
                a.dup() + a[2:]]

    if a.cmp(b) < 0:
        # keep value for ValueRange
        return [a.dup() + a[2:],
                None]

    # keep value for ValueRange
    rst = [None, None]

    if a.cmp_left(b[0]) < 0:
        o = [a[0], b.prev_right()] + a[2:]
        rst[0] = a.__class__(*o)

    if b.cmp_right(a[1]) < 0:
        o = [b.next_left(), a[1]] + a[2:]
        rst[1] = a.__class__(*o)

    return rst


def bisect_left(a, x, lo=0, hi=None):

    # Find the left-most i so that a[i] >= x
    # Thus i is where to a.insert(i, x)

    if lo < 0:
        raise ValueError('lo must be non-negative')

    if hi is None:
        hi = len(a)

    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid].cmp(x) < 0:
            lo = mid + 1
        else:
            hi = mid
    return lo


def assert_compatible(l, r):
    if not is_compatible(l, r):
        raise TypeError('{l} {ltyp} is incompatible with {r} {rtyp}'.format(
            l=l, ltyp=type(l), r=r, rtyp=type(r)))


def is_compatible(l, r):
    if l is None or r is None:
        return True

    if type(l) in compatible_types.get(type(r), ()):
        return True

    if type(r) in compatible_types.get(type(l), ()):
        return True

    return False
