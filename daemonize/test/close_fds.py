import os
import sys

import daemonize
from pykit import proc

foo_fn = '/tmp/foo'
bar_fn = '/tmp/bar'
pidfn = '/tmp/test_daemonize.pid'


def write_file(fn, cont):
    try:
        with open(fn, 'w') as f:
            f.write(cont)
    except Exception as e:
        print repr(e) + ' while write_file:' + fn
        raise


def run():
    code, out, err = proc.shell_script('/usr/sbin/lsof -p ' + str(os.getpid()))
    write_file(foo_fn, repr(out))


if __name__ == '__main__':

    fd = open(bar_fn, 'w')
    op = sys.argv[1]
    sys.argv[1] = 'start'
    if op == 'close':
        daemonize.daemonize_cli(run, pidfn, close_fds=True)
    else:
        daemonize.daemonize_cli(run, pidfn, close_fds=False)
