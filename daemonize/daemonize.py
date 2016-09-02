import errno
import fcntl
import os
import signal
import sys
import time
import traceback

import fs
import genlog
import sockinherit

logger = logging.getLogger(__name__)


class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """

    def __init__(self, pidfile, run=lambda: None,
                 stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', foreground=False):

        self._run = run
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        # NOTE: We need to open another separate file to avoid the file
        #       reopened # again. Which case, process lose file lock.
        #
        # From "man fcntl":
        # As well as being removed by an explicit F_UNLCK, record locks are
        # automatically released when the process terminates  or  if  it
        # closes  any  file descriptor  referring  to  a  file  on which locks
        # are held.  This is bad: it means that a process can lose the locks
        # on a file like /etc/passwd or /etc/mtab when for some reason a
        # library function decides to open, read and close it.
        self.lockfile = pidfile + ".lock"
        self.lockfp = None
        self.foreground = foreground

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """

        if self.foreground:
            return

        try:

            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)

        except OSError as e:

            sys.stderr.write("fork #1 failed: %d (%s)\n"
                             % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        # os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:

            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)

        except OSError as e:

            sys.stderr.write("fork #2 failed: %d (%s)\n"
                             % (e.errno, e.strerror))
            sys.exit(1)

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
        self.run()

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
            logger.error('write pid failed.' + repr(e))
            sys.exit(0)

    def stop_pid(self):
        return self.stop()

    def stop(self):

        pid = None
        if not os.path.exists(self.pidfile):

            logger.debug('pidfile not exist:' + self.pidfile)
            return

        while 1:

            try:
                pid = fs.read_file(self.pidfile)
                pid = int(pid)
                os.kill(pid, signal.SIGTERM)
                return

            except Exception as e:
                logger.debug('get pid failed.' + str(e) + str(pid))
                # file been deleted?
                break

            time.sleep(0.1)

    def restart(self):
        """
        Restart the daemon
        """

        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been
        daemonized by start() or restart().
        """

        self._run()

        return


def standard_daemonize(run_func, pidfn,
                       inheritable=None,
                       upgrade_arg=None,
                       cleanup=None):

    d = Daemon(pidfn, None)

    logger.info("sys.argv: " + repr(sys.argv))

    try:
        if len(sys.argv) == 1:
            d.init_proc()
            run_func()

        elif len(sys.argv) == 2:

            if 'start' == sys.argv[1]:
                d.daemonize()
                if inheritable is not None:
                    sockinherit.init_inheritable(inheritable)
                    install_upgrade_sig(d, inheritable, upgrade_arg, cleanup)

                d.init_proc()
                run_func()

            elif 'stop' == sys.argv[1]:
                d.stop_pid()

            elif 'restart' == sys.argv[1]:
                if inheritable is None:
                    d.stop_pid()
                    d.daemonize()
                    d.init_proc()
                else:
                    signal_to_upgrade(pidfn)
                    # if it returns, upgrade failed. fall back to normal
                    # restart.

                    d.stop_pid()

                    d.daemonize()
                    sockinherit.init_inheritable(inheritable)
                    install_upgrade_sig(d, inheritable, upgrade_arg, cleanup)
                    d.init_proc()

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
        logger.error(traceback.format_exc())
        logger.error(repr(e))


def signal_to_upgrade(pidFile):

    pid = _get_pid(pidFile)
    logger.info("old pid: " + repr(pid))

    if pid is not None:

        try:
            os.kill(pid, signal.SIGUSR2)
        except OSError:
            # no such process
            return

        logger.info("SIGUSR2 sent to: " + repr(pid))

        for ii in range(30):
            time.sleep(0.1)
            pid2 = _get_pid(pidFile)
            if pid2 is not None and pid != pid2:
                logger.info("new pid generated, upgrade succeed: "
                            + repr(pid2))
                sys.exit(0)


def _get_pid(fn):

    try:
        with open(fn, 'r') as f:
            cont = f.read()
    except OSError:
        return None

    try:
        return int(cont)
    except ValueError:
        return None


def install_upgrade_sig(d, inheritable, upgrade_arg, cleanup):

    heir = {}
    for name, val in inheritable.items():
        heir[name] = val['sock'].fileno()

    def sig_up(*args, **argkv):
        if callable(upgrade_arg):
            exe, args, cwd = upgrade_arg()
        else:
            exe, args, cwd = upgrade_arg

        sockinherit.upgrade(exe, args, cwd, heir)

        logger.info("parent spwaned new process")
        logger.info("parent sleep 1 second")
        time.sleep(1)

        d.unlock()
        logger.info("parent released lock, about to exit")

        (cleanup or sys.exit)()

    signal.signal(signal.SIGUSR2, sig_up)
