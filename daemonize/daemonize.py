import os
import sys
import time
import traceback
from signal import SIGTERM

import conf
import genlog
import util


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

        except OSError, e:

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

        except OSError, e:

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

    def delpid(self):

        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        self.daemonize()

        # Check for a pidfile to see if the daemon already runs
        try:
            self.lockfp = util.open_lock_file(self.lockfile)
        except util.FileLockError:
            message = "pidfile %s locked. Daemon already running?\n"
            genlog.logger.debug(message % self.pidfile)
            sys.exit(1)
        except Exception as e:
            genlog.logger.error('open_lock_file failed.' + str(e))
            sys.exit(0)

        self.pf = open(self.pidfile, 'w+r')
        pf = self.pf

        try:
            pid = os.getpid()
            genlog.logger.debug('write pid:' + str(pid))
            pf.truncate(0)
            pf.write(str(pid))
            pf.flush()
        except Exception as e:
            genlog.logger.error('write pid failed.' + repr(e))
            sys.exit(0)


        self.run()

    def stop(self):

        pid = None
        if not os.path.exists(self.pidfile):

            genlog.logger.debug('pidfile not exist:' + self.pidfile)
            return

        while 1:

            try:
                pid = util.read_file(self.pidfile)
                pid = int(pid)
                os.kill(pid, SIGTERM)
                return

            except Exception as e:
                genlog.logger.debug('get pid failed.' + str(e) + str(pid))
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


def standard_daemonize(run_func, pidFile):
    import inspect
    frame = inspect.currentframe(1)
    info = inspect.getframeinfo(frame)

    try:
        if len(sys.argv) == 1:
            genlog.logger.debug(
                '---- foreground running %s ----' % (info.filename))

            Daemon(pidFile, run_func, foreground=True).start()

        elif len(sys.argv) == 2:
            genlog.logger.debug('---- %sing %s ----' %
                                (sys.argv[1], info.filename))

            if 'start' == sys.argv[1]:
                Daemon(pidFile, run_func).start()

            elif 'stop' == sys.argv[1]:
                Daemon(pidFile, run_func).stop()

            elif 'restart' == sys.argv[1]:
                Daemon(pidFile, run_func).restart()

            else:
                genlog.logger.error("Unknown command : " % (sys.argv[1]))
                print "Unknown command"
                sys.exit(2)

            sys.exit(0)
        else:
            print "usage: %s start|stop|restart" % sys.argv[0]
            sys.exit(2)

    except Exception as e:
        genlog.logger.debug(traceback.format_exc())
        genlog.logger.error(repr(e))
