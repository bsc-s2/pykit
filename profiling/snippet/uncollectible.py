from __future__ import print_function

import gc


'''
This snippet shows how to create a uncollectible object:
It is an object in a cycle reference chain, in which there is an object
with __del__ defined.
The simpliest is an object that refers to itself and with a __del__ defined.

    > python uncollectible.py

    ======= collectible object =======

    *** init,     nr of referrers: 4
                  garbage:         []
                  created:         collectible: <__main__.One object at 0x102c01090>
                  nr of referrers: 5
                  delete:
    *** __del__ called
    *** after gc, nr of referrers: 4
                  garbage:         []

    ======= uncollectible object =======

    *** init,     nr of referrers: 4
                  garbage:         []
                  created:         uncollectible: <__main__.One object at 0x102c01110>
                  nr of referrers: 5
                  delete:
    *** after gc, nr of referrers: 5
                  garbage:         [<__main__.One object at 0x102c01110>]

'''


def dd(*msg):
    for m in msg:
        print(m, end='')
    print()


class One(object):

    def __init__(self, collectible):
        if collectible:
            self.typ = 'collectible'
        else:
            self.typ = 'uncollectible'

            # Make a reference to it self, to form a reference cycle.
            # A reference cycle with __del__, makes it uncollectible.
            self.me = self

    def __del__(self):
        dd('*** __del__ called')


def test_it(collectible):

    dd()
    dd('======= ', ('collectible' if collectible else 'uncollectible'), ' object =======')
    dd()

    gc.collect()
    dd('*** init,     nr of referrers: ', len(gc.get_referrers(One)))
    dd('              garbage:         ', gc.garbage)

    one = One(collectible)
    dd('              created:         ', one.typ, ': ', one)
    dd('              nr of referrers: ', len(gc.get_referrers(One)))

    dd('              delete:')
    del one

    gc.collect()

    dd('*** after gc, nr of referrers: ', len(gc.get_referrers(One)))
    dd('              garbage:         ', gc.garbage)


if __name__ == "__main__":
    test_it(collectible=True)
    test_it(collectible=False)
