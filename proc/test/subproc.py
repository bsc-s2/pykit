import os
import sys

code = int(sys.argv[1])

os.write(1, "out-1\n")
os.write(1, "out-2\n")

os.write(2, "err-1\n")
os.write(2, "err-2\n")

sys.exit(code)
