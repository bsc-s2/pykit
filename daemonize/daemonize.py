import os
import sys
import time
import traceback
from signal import SIGTERM

import conf
import genlog
import util

logger = genlog.logger


class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """

    def __init__(self, pidfile, run=lambda: None,
                 stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):

        self._run = run
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

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
            pf = util.open_lock_file(self.pidfile)
        except util.FileLockError:
            message = "pidfile %s locked. Daemon already running?\n"
            logger.debug(message % self.pidfile)
            sys.exit(1)
        except Exception as e:
            logger.debug('open_lock_file failed.' + str(e))
            sys.exit(0)

        try:
            pid = os.getpid()
            logger.debug('write pid:' + str(pid))
            pf.truncate(0)
            pf.write(str(pid))
            pf.flush()
        except Exception as e:
            logger.debug('write pid failed.' + str(e))
            sys.exit(0)

        self.run()

    def stop(self):

        pid = None
        if not os.path.exists(self.pidfile):

            # pidfile not exist, just return
            return

        while 1:
            try:
                pf = util.open_lock_file(self.pidfile)
            except util.FileLockError:
                logger.debug('file locked, daemon is running.')
                pf = None
            except Exception as e:
                logger.debug('open_lock_file failed.')
                sys.exit(0)

            # daemon runing, do kill
            if pf == None:
                logger.debug('kill pid:' + str(pid))
                if pid == None:
                    try:
                        pid = util.read_file(self.pidfile)
                        pid = int(pid)
                    except OSError, err:
                        err = str(err)
                        if err.find("No such process") > 0:
                            # process killed already?
                            break
                        else:
                            logger.debug(str(err))
                            sys.exit(1)

                    except Exception as e:
                        logger.debug('get pid failed.' + str(e) + str(pid))
                        # file been deleted?
                        break

                os.kill(pid, SIGTERM)
                time.sleep(0.1)
                continue
            else:
                # locked, Daemon should been killed.
                pf.close()
                break

        return

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

    logger.debug('----%s runs----' % (info.filename))
    logger.debug(str(sys.argv))

    try:
        if len(sys.argv) == 1:
            run_func()

        if len(sys.argv) == 2:
            if 'start' == sys.argv[1]:
                logger.debug('start')
                Daemon(pidFile, run_func).start()

            elif 'stop' == sys.argv[1]:
                Daemon(pidFile, run_func).stop()

            elif 'restart' == sys.argv[1]:
                Daemon(pidFile, run_func).restart()

            else:
                logger.debug("Unknown command : " % (sys.argv[1]))
                print "Unknown command"
                sys.exit(2)

            sys.exit(0)
        else:
            print "usage: %s start|stop|restart" % sys.argv[0]
            sys.exit(2)

    except Exception as e:
        logger.warn(traceback.format_exc())
