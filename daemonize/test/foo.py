import time

import daemonize

fn = '/tmp/foo'
pidfn = '/tmp/test_daemonize.pid'


def write_file(fn, cont):
    with open(fn, 'w') as f:
        f.write(cont)


def run():

    write_file(fn, 'foo-before')

    time.sleep(1)

    write_file(fn, 'foo-after')


daemonize.daemonize_cli(run, pidfn)
