import argparse
import os
import sys

from . import portlock
from .. import proc

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='portlock tool')

    parser.add_argument('--lock',    '-l', type=str,   action='store', help='lock name')
    parser.add_argument('--timeout', '-t', type=float, action='store', help='lock wait timeout, in second')
    parser.add_argument('--script',  '-c', type=str,   action='store', help='execute a script in string')
    parser.add_argument('command',         type=str, nargs='*',        help='shell command to execute')

    args = parser.parse_args()

    timeout = args.timeout
    if timeout is None:
        timeout = 1

    try:
        with portlock.Portlock(args.lock, timeout=timeout):

            if args.script is not None:
                rc, out, err = proc.shell_script(args.script)
            else:
                rc, out, err = proc.command(*args.command)

            os.write(1, out)
            os.write(2, err)
            sys.exit(rc)

    except portlock.PortlockTimeout as e:
        os.write(2, 'portlock {lock} timeout: {timeout} sec'.format(
                lock=args.lock,
                timeout=timeout))
        sys.exit(1)
