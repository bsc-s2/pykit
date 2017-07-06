#######################
# unit test case read this file
import os
import sys

fd = int(sys.argv[1])

try:
    a = os.read(fd, 3)
    print a
    sys.exit(0)
except OSError as e:
    print 'errno=' + str(e.errno)
    sys.exit(1)
