from pykit import dictutil


class TrieNode(dict):

    def __init__(self, *args, **kwargs):
        super(TrieNode, self).__init__(*args, **kwargs)

        # Total number of items with the prefix represented by this node.
        # `None` means there might be more items with this prefix thus its
        # number can not be decided yet.
        self.n = None

        # Trie branch key, a single char
        self.char = ''

        # An outstanding node is a node that there might be more following input
        # string which has its corresponding prefix.
        self.outstanding = None

        # If this node is an outstanding node to its parent node.
        # When created, a node must be an outstanding node.
        self.is_outstanding = True

        # If this node is an end of a line of string.
        # A leaf node must be an eol node.
        # But not vice verse
        self.is_eol = False

    def __str__(self):

        children_keys = sorted(self.keys())

        if self.is_outstanding:
            mark = '*'
        else:
            mark = ' '

        if self.char != '':
            c = str(self.char) + ','
        else:
            c = ''

        if len(children_keys) > 0:
            colon = ': '
        else:
            colon = ''

        line = '{mark}{c}{n}{colon}'.format(c=c, n=(self.n or '?'), mark=mark, colon=colon)

        fields = []
        for c in children_keys:
            substr = str(self[c])
            indent = ' ' * len(line)
            substr = indent + substr.replace('\n', '\n' + indent)

            fields.append(substr)

        rst = '\n'.join(fields)
        return line + rst[len(line):]


def _trie_node(parent, char):
    n = TrieNode()
    n.char = char
    parent.outstanding = n
    return n


def make_trie(sorted_iterable, node_max_num=1):

    t = TrieNode()

    for _s in sorted_iterable:

        # find longest common prefix of _s and any seen string
        node = t
        for i, c in enumerate(_s):
            if c in node:
                node = node[c]
            else:
                break

        # `node` now is at where the longest common prefix.
        # `i` points to next char not in common prefix in `_s`.

        # Since `node` is the longest prefix and all input strings are sorted,
        # the prefix represented by the child `node.outstanding` can never be a prefix of
        # any following strings.
        _squash(node.outstanding, node_max_num)

        for c in _s[i:]:
            node[c] = _trie_node(node, c)
            node = node[c]

        node.is_eol = True

        # Only leaf node is count by 1
        node.n = 1

    _squash(t, node_max_num)

    return t


def sharding(sorted_iterable, size, accuracy=None, joiner=''.join):

    if accuracy is None:
        accuracy = size / 10

    t = make_trie(sorted_iterable, node_max_num=accuracy)

    n = 0
    prev_key = None
    rst = []

    # iterate root node.
    t = {'':t}

    for ks, node in dictutil.depth_iter(t, is_allowed=lambda ks, v: v.is_eol or len(v) == 0):

        if n >= size:

            rst.append((prev_key, n))

            # strip empty root path
            prev_key = ks[1:]
            prev_key = joiner(prev_key)
            n = 0

        if len(node) == 0:
            n += node.n
        else:
            # node.is_eol == True
            n += 1

    rst.append((prev_key, n))

    return rst


def _squash(node, node_max_num):

    # If the number of strings with prefix at `node`(children of `node`) is smaller than `node_max_num`,
    # squash all children to reduce memory cost.

    if node is None:
        return

    _squash(node.outstanding, node_max_num)

    total = node.n or 0
    for subnode in node.values():
        total += subnode.n

    if total <= node_max_num:
        for c in node.keys():
            del node[c]

    node.n = total
    node.is_outstanding = False
