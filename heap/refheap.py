
# index is started from 1.
#
#          1
#     2          3
#   4    5     6    7
#                            level
#          1                   0
#    10         11             1
# 100  101   110  111          2
#
# - On each level, widths of level in binary number are the same and just equals level+1.
# - The most significant bit are always 1.
# - The 2nd significant bit indicate it is on left(0) or right(1) level-1 sub-heap.
# - The 3rd significant bit indicate it is on left(0) or right(1) level-2 sub-heap.
# - ...

primitive_types = (type(None), int, long, bool, basestring, tuple, float, complex)


class HeapError(Exception):
    pass


class Duplicate(HeapError):
    pass


class Empty(HeapError):
    pass


class NotFound(HeapError):
    pass


class Node(list):

    # node in heap:
    # node[0] is left child
    # node[1] is right child

    def __init__(self, userdata):

        super(Node, self).__init__([None, None])

        self.parent = None
        self.userdata = userdata

    def min_child(self):
        if self[0] is None:
            return self[1]

        if self[1] is None:
            return self[0]

        if self[0].userdata < self[1].userdata:
            return self[0]
        else:
            return self[1]

    def __lt__(self, b):
        return self.userdata < b.userdata

    def __str__(self):

        ud_str = str(self.userdata)

        mark = '> '
        width = 16
        item_width = width + len(mark)

        ud_str = ('{0:>' + str(width) + '}').format(ud_str)
        ud_str = ud_str + mark

        if self == [None, None]:
            return ud_str

        if self[0] is None:
            sl = ['-']
        else:
            sl = str(self[0]).split('\n')
        if self[1] is None:
            sr = ['-']
        else:
            sr = str(self[1]).split('\n')

        sl = [' ' * item_width + x for x in sl]
        sr = [' ' * item_width + x for x in sr]
        sl[0] = ud_str + sl[0][item_width:]

        return '\n'.join(sl) + '\n' + '\n'.join(sr)


# wrapper of primitive type
class Primitive(object):

    def __init__(self, obj):
        self.data = obj

    def __str__(self):
        return str(self.data)

    def __lt__(self, b):
        return self.data < b.data


class RefHeap(object):

    def __init__(self, iterable=()):
        self.size = 0
        self.root = None

        # map user data `obj` to heap node instance.
        self.userdata_map = {}

        for i in iterable:
            self.push(i)

    def push(self, obj):
        # wrap primitive type with an object or no duplicate can be added

        if isinstance(obj, primitive_types):
            obj = Primitive(obj)

        obj_id = id(obj)

        if obj_id in self.userdata_map:
            raise Duplicate('object is already in heap')

        node = Node(obj)
        self.userdata_map[obj_id] = node

        self.size += 1

        if self.size == 1:
            self.root = node
            return

        pos = self.size

        p = self.node_at(_parent_index(pos))

        p[_child_lr_idx(pos)] = node
        node.parent = p

        self._sift(node)

    def get(self):
        self.assert_not_empty()
        return self.return_val(self.root)

    def pop(self):
        self.assert_not_empty()
        return self.remove_node(self.root)

    def pop_all(self, map=lambda x: x):
        rst = []
        while self.size > 0:
            rst.append(map(self.pop()))
        return rst

    def remove(self, obj):
        node = self._get_object_node(obj)
        return self.remove_node(node)

    def remove_node(self, node):

        rst = self.return_val(node)

        last = self.node_at(self.size)

        self.swap(node, last)
        self.remove_last(last)
        self._sift(node)

        if self.size == 0:
            self.root = None

        return rst

    def sift(self, obj):
        if isinstance(obj, primitive_types):
            raise ValueError('primitive type does not support sift, just replace it')

        node = self._get_object_node(obj)
        return self._sift(node)

    def _get_object_node(self, obj):
        if id(obj) not in self.userdata_map:
            raise NotFound('object is not found in heap, id:' + str(obj))

        node = self.userdata_map[id(obj)]
        return node

    def _sift(self, node):

        x = node.userdata
        xid = id(x)

        # upwards
        up = False
        while (node.parent is not None
               and x < node.parent.userdata):

            # move parent down to node
            self.userdata_map[id(node.parent.userdata)] = node
            node.userdata = node.parent.userdata

            node = node.parent
            up = True

        node.userdata = x
        self.userdata_map[xid] = node

        if up:
            return

        # downwards
        while True:

            _min = node.min_child()
            if _min is None or not (_min.userdata < x):
                break

            # move _min up to node
            self.userdata_map[id(_min.userdata)] = node
            node.userdata = _min.userdata

            node = _min

        node.userdata = x
        self.userdata_map[xid] = node

    def swap(self, a, b):
        # we do not swap node, but exchange node.userdata only.
        self.userdata_map[id(a.userdata)], self.userdata_map[id(b.userdata)] = b, a
        a.userdata, b.userdata = b.userdata, a.userdata

    def remove_last(self, last):
        if last.parent is not None:
            last.parent[_child_lr_idx(self.size)] = None
        last.parent = None

        del self.userdata_map[id(last.userdata)]
        last.userdata = None

        self.size -= 1

    def return_val(self, node):
        rst = node.userdata
        if isinstance(rst, Primitive):
            rst = rst.data
        return rst

    def node_at(self, idx):

        # idx starts from 1

        p = self.root
        lvl = index_level(idx)

        for l in range(lvl - 1, -1, -1):
            lr = (idx >> l) & 1
            p = p[lr]

        return p

    def assert_not_empty(self):
        if self.size == 0:
            raise Empty()

    def __str__(self):
        return str(self.root)


def index_level(idx):

    # root is at level 0

    lvl = 0
    while idx > 1:
        idx = _parent_index(idx)
        lvl += 1

    return lvl


def _parent_index(c):
    return c // 2


def _child_lr_idx(idx):
    return idx % 2
