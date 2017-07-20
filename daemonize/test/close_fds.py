import daemonize
import os
import sys

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

    names = []

    fd_path = '/proc/' + str(os.getpid()) + '/fd'
    for n in os.listdir(fd_path):
        try:
            dst = os.readlink(fd_path + '/' + n)
            names.append(dst)
        except:
            pass

    write_file(foo_fn, ''.join(names))


if __name__ == '__main__':

    fd = open(bar_fn, 'w')
    op = sys.argv[1]
    sys.argv[1] = 'start'
    if op == 'close':
        daemonize.daemonize_cli(run, pidfn, close_fds=True)
    else:
        daemonize.daemonize_cli(run, pidfn, close_fds=False)
