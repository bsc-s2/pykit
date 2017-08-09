import errno
import fcntl
import logging
import os
import signal
import sys
import time

import __main__

logger = logging.getLogger(__name__)


class Daemon(object):

    def __init__(self,
                 pidfile=None,
                 stdin='/dev/null',
                 stdout='/dev/null',
                 stderr='/dev/null',
                 close_fds=False):

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile or _default_pid_file()
        # NOTE: We need to open another separate file to avoid the file
        #       being reopened again.
        #       In which case, process loses file lock.
        #
        # From "man fcntl":
        # As well as being removed by an explicit F_UNLCK, record locks are
        # automatically released when the process terminates or if it
        # closes any file descriptor referring to a file on which locks
        # are held. This is bad: it means that a process can lose the locks
        # on a file like /etc/passwd or /etc/mtab when for some reason a
        # library function decides to open, read and close it.
        self.lockfile = self.pidfile + ".lock"
        self.lockfp = None
        self.close_fds = close_fds

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """

        try:

            pid = os.fork()
            if pid > 0:
                # exit first parent
                _close_std_io()
                sys.exit(0)

        except OSError as e:
            logger.error("fork #1 failed: " + repr(e))
            sys.exit(1)

        # decouple from parent environment
        os.setsid()
        os.umask(0)

        # do second fork
        try:

            pid = os.fork()
            if pid > 0:
                # exit from second parent
                _close_std_io()
                sys.exit(0)

        except OSError as e:
            logger.error("fork #2 failed: " + repr(e))
            sys.exit(1)

        if self.close_fds:
            _close_fds()

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        logger.info("OK daemonized")

    def trylock_or_exit(self, timeout=10):

        interval = 0.1
        n = int(timeout / interval) + 1
        flag = fcntl.LOCK_EX | fcntl.LOCK_NB

        for ii in range(n):

            fd = os.open(self.lockfile, os.O_RDWR | os.O_CREAT)

            fcntl.fcntl(fd, fcntl.F_SETFD,
                        fcntl.fcntl(fd, fcntl.F_GETFD, 0)
                        | fcntl.FD_CLOEXEC)

            try:
                fcntl.lockf(fd, flag)

                self.lockfp = os.fdopen(fd, 'w+r')
                break

            except IOError as e:
                os.close(fd)
                if e[0] == errno.EAGAIN:
                    time.sleep(interval)
                else:
                    raise

        else:
            logger.info("Failure acquiring lock %s" % (self.lockfile, ))
            sys.exit(1)

        logger.info("OK acquired lock %s" % (self.lockfile))

    def unlock(self):

        if self.lockfp is None:
            return

        fd = self.lockfp.fileno()
        fcntl.lockf(fd, fcntl.LOCK_UN)
        self.lockfp.close()
        self.lockfp = None

    def start(self):

        self.daemonize()
        self.init_proc()

    def init_proc(self):
        self.trylock_or_exit()
        self.write_pid_or_exit()

    def write_pid_or_exit(self):

        self.pf = open(self.pidfile, 'w+r')
        pf = self.pf

        fd = pf.fileno()
        fcntl.fcntl(fd, fcntl.F_SETFD,
                    fcntl.fcntl(fd, fcntl.F_GETFD, 0)
                    | fcntl.FD_CLOEXEC)

        try:
            pid = os.getpid()
            logger.debug('write pid:' + str(pid))

            pf.truncate(0)
            pf.write(str(pid))
            pf.flush()
        except Exception as e:
            logger.exception('write pid failed.' + repr(e))
            sys.exit(0)

    def stop(self):

        pid = None

        if not os.path.exists(self.pidfile):

            logger.debug('pidfile not exist:' + self.pidfile)
            return

        try:
            pid = _read_file(self.pidfile)
            pid = int(pid)
            os.kill(pid, signal.SIGTERM)
            return

        except Exception as e:
            logger.warn('{e} while get and kill pid={pid}'.format(
                e=repr(e), pid=pid))


def _read_file(fn):
    with open(fn, 'r') as f:
        return f.read()


def _close_std_io():
    os.close(0)
    os.close(1)
    os.close(2)


def _close_fds():

    try:
        max_fd = os.sysconf("SC_OPEN_MAX")
    except ValueError as e:
        logger.warn(repr(e) + ' while get max fds of a process')
        max_fd = 65536

    for i in xrange(3, max_fd):
        try:
            os.close(i)
        except OSError:
            pass


def _default_pid_file():

    if hasattr(__main__, '__file__'):
        name = __main__.__file__
        name = os.path.basename(name)
        if name == '<stdin>':
            name = '__stdin__'
        return '/var/run/' + name.rsplit('.', 1)[0]
    else:
        return '/var/run/pykit.daemonize'


def daemonize_cli(run_func, pidfn, close_fds=False):

    logging.basicConfig(stream=sys.stderr)
    logging.getLogger(__name__).setLevel(logging.DEBUG)

    d = Daemon(pidfile=pidfn, close_fds=close_fds)

    logger.info("sys.argv: " + repr(sys.argv))

    try:
        if len(sys.argv) == 1:
            d.init_proc()
            run_func()

        elif len(sys.argv) == 2:

            if 'start' == sys.argv[1]:
                d.start()
                run_func()

            elif 'stop' == sys.argv[1]:
                d.stop()

            elif 'restart' == sys.argv[1]:
                d.stop()
                d.start()
                run_func()

            else:
                logger.error("Unknown command: %s" % (sys.argv[1]))
                print "Unknown command"
                sys.exit(2)

            sys.exit(0)
        else:
            print "usage: %s start|stop|restart" % sys.argv[0]
            sys.exit(2)

    except Exception as e:
        logger.exception(repr(e))


standard_daemonize = daemonize_cli
