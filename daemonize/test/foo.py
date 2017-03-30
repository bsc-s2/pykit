import time

import daemonize

fn = '/tmp/foo'
pidfn = '/tmp/test_daemonize.pid'


def write_file(fn, cont):
    try:
        with open(fn, 'w') as f:
            f.write(cont)
    except Exception as e:
        print repr(e) + ' while write_file:' + fn
        raise


def run():

    write_file(fn, 'foo-before')

    time.sleep(1)

    write_file(fn, 'foo-after')


daemonize.daemonize_cli(run, pidfn)
