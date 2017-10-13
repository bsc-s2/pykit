import sys

from pykit import fsutil

fn = sys.argv[1]
for x in fsutil.Cat(fn, strip=True).iterate(timeout=0):
    print x
