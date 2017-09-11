

list_like = (type([]), type(()))

compatible_types = {
    type(None): [type(None)],
    int:        [type(None), int, ],
    long:       [type(None), int,   long, ],
    float:      [type(None), int,   long, float, ],
    str:        [type(None), str, ],
    tuple:      [type(None), tuple, ],
    list:       [type(None), list, ],
}


class RangeException(Exception):
    pass


class Unmergeable(RangeException):
    pass


class Range(list):

    def __init__(self, left, right, element_type=None):

        if element_type is None:
            val = left
            if val is None:
                val = right
            if val is None:
                val = 1
            element_type = type(val)

        assert_type_valid(element_type)

        self.element_type = element_type

        compatible = compatible_types[self.element_type]

        if type(left) not in compatible:
            raise TypeError('left {l} is incompatible with {typ}'.format(
                l=type(left), typ=self.element_type))

        if type(right) not in compatible:
            raise TypeError('right {r} is incompatible with {typ}'.format(
                r=type(right), typ=self.element_type))

        if (left is not None
            and right is not None
                and left > right):
            raise ValueError('left not smaller or equal right: {left}, {right}'.format(
                left=left, right=right))

        super(Range, self).__init__([left, right])

    def cmp(self, b):

        # if a and b can be merged into one range, we say a == b

        if (self[0] is not None
            and b[1] is not None
                and self[0] > b[1]):
            return 1

        if (self[1] is not None
            and b[0] is not None
                and self[1] < b[0]):
            return -1

        # incomparable: overlapping or adjacent ranges
        return 0

    def is_adjacent(self, b):
        return self[1] == b[0]

    def has(self, val):
        return (self[0] is None or self[0] <= val) and (self[1] is None or self[1] > val)


class RangeSet(list):

    def __init__(self, iterable=None, element_type=int):

        assert_type_valid(element_type)

        if iterable is None:
            iterable = []

        super(RangeSet, self).__init__([Range(x[0], x[1], element_type=element_type)
                                        for x in iterable])

        for i in range(0, len(self) - 1):
            if self[i].cmp(self[i + 1]) != -1:
                raise ValueError('range[{i}] {ri} does not smaller than range[{j}] {ripp}'.format(
                    i=i,
                    j=i + 1,
                    ri=self[i],
                    ripp=self[i + 1],
                ))

        self.element_type = element_type

    def add(self, rng):

        if not isinstance(rng, (list, tuple, Range)):
            raise TypeError('invalid range {rng} of type {typ}'.format(
                rng=rng, typ=type(rng)))

        if len(rng) != 2:
            raise ValueError('range length is not 2 but {l}: {rng}'.format(
                l=len(rng), rng=rng))

        rng = Range(rng[0], rng[1], element_type=self.element_type)

        if len(self) == 0:
            self.insert(0, rng)
            return

        i = bisect_left(self, rng)

        while i < len(self):
            if rng.cmp(self[i]) == 0:
                rng = merge_range(rng, self[i])
                self.pop(i)
            else:
                break

        self.insert(i, rng)

    def has(self, val):
        rng = Range(val, val, element_type=self.element_type)
        i = bisect_left(self, rng)

        if i == len(self):
            return False

        return self[i].has(val)


def assert_type_valid(typ):
    if typ not in compatible_types:
        raise TypeError('{typ} is not comparable'.format(typ=typ))


def merge_range(a, b):

    assert a.element_type == b.element_type

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

    return Range(left, right, element_type=a.element_type)


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
