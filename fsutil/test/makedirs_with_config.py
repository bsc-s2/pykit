import os
import sys

from pykit import fsutil

fn = sys.argv[1]

fsutil.makedirs(fn)
stat = os.stat(fn)
os.write(1, '{uid},{gid}'.format(uid=stat.st_uid, gid=stat.st_gid))
