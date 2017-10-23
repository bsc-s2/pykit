#!/usr/bin/env python
# coding: utf-8

import random

rate = 0.5
init_res = 1.0


def rand_n_times(n_rounds, a, b):
    return [random.random() * (b - a) + a for _ in range(n_rounds)]


def get_resource(left):
    # each node provides 1.0 resources
    return left * rate + init_res * n_nodes


def rr(lst):
    lst = ['{0:.3f}'.format(x) for x in lst]
    return ' '.join(lst)

# range of resource required for each node
required_range = [ (.2, .5), (1.1, 1.5), ]

# uncomment to see: equal loads but either can be fully satisfied
# required_range = [ (1.2, 1.5), (1.2, 1.5), ]

# uncomment to see: equal loads and both can be satisfied
# required_range = [ (.2, 1.0), (.2, 1.0), ]

n_nodes = len(required_range)
n_rounds = 50
width = 10

# accesses[node_index][round_index] means how much resource a node requires
accesses = [rand_n_times(n_rounds, lft, rt)
            for lft, rt in required_range]

# uncomment to customize required resource.
accesses = [
        [.1] * 10 + [2.0] * 10 + [0.1] * 10,
        [.2] * 10 + [1.0] * 10 + [0.5] * 10,
]
# accesses = [
        # [1] * 30,
        # [1] * 30,
# ]

nodes_allocated = [init_res] * n_nodes

print 'Emulation of resource limitation in a cluster of two node.'
print 'Different node could have different resource requirement.'
print 'This emulation shows how resource are dynamically allocated according to node requirements.'
print
print 'format for each node:'
print '     <consumed>/<allocated> <consumption illustration>'

print 'symbols:'
print '     `c`: consumed'
print '     `l`: left'
print '     `.`: required but not satisfied'
print 'thus:'
print '     required = `c` + `.`'
print '     allocated = `c` + `l`'
print

print 'randomized required resource for each node:'
for i, (lft, rt) in enumerate(required_range):
    print '{0:<50}'.format(
        '{lft} ~ {rt}'.format(lft=lft, rt=rt)
    ),
print
print


for i in range(len(accesses[0])):
    total_left = 0
    nodes_consumed = []

    # emulation of one round for each node
    for j, allocated in enumerate(nodes_allocated[:]):

        required = accesses[j][i]

        consumed = min([allocated, required])
        left = allocated - consumed

        sym = '{0:.2f}/{1:.2f} '.format(consumed, allocated)
        sym += 'c' * int(consumed * width) + 'l' * int(left * width)
        if required > allocated:
            sym += '.' * int((required - allocated) * width)
        print '{sym:<50}'.format(sym=sym),

        total_left += left
        nodes_consumed.append(required)
    print

    total_resource_for_next = get_resource(total_left)

    total_consumed = sum(nodes_consumed)
    total_allocated = sum(nodes_allocated)

    for j, alc in enumerate(nodes_allocated):

        # Adjust node weight according to its actual consumed resource.
        # But adjust it slowly.
        _current_weight = float(alc) / total_allocated
        _expected_weight = float(nodes_consumed[j]) / total_consumed

        _next_weight = _current_weight * .5 + _expected_weight * .5

        nodes_allocated[j] = total_resource_for_next * _next_weight
