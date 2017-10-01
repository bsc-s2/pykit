
import errno
import hashlib
import logging
import platform
import socket
import threading
import time

OS = platform.system()

PORT_N = 3
PORT_RANGE = (40000, 60000)

DEFAULT_SLEEP_TIME = 0.01  # sec

logger = logging.getLogger(__name__)


class PortlockError(Exception):
    pass


class PortlockTimeout(PortlockError):
    pass


class Portlock(object):

    def __init__(self, key, timeout=1, sleep_time=None):

        self.key = key
        self.addr = str_to_addr(key)
        self.timeout = timeout
        self.sleep_time = sleep_time or DEFAULT_SLEEP_TIME
        self.socks = [None] * PORT_N

        self.thread_lock = threading.RLock()

    def try_lock(self):

        self.thread_lock.acquire()

        try:
            self._lock()

            if self.has_locked():
                return True
            else:
                self.socks = [None] * PORT_N
                self.thread_lock.release()
                return False

        except Exception:
            self.thread_lock.release()
            raise

    def has_locked(self):

        if OS == 'Linux':
            return self.socks[0] is not None

        # other OS

        return len([x for x in self.socks
                    if x is not None]) > len(self.socks) / 2

    def acquire(self):

        t0 = time.time()

        while True:

            if self.try_lock():
                return

            now = time.time()
            left = t0 + self.timeout - now
            if left > 0:
                slp = min([self.sleep_time, left + 0.001])
                time.sleep(slp)
            else:
                raise PortlockTimeout(
                    'portlock timeout: ' + repr(self.key), self.key)

    def release(self):

        if not self.has_locked():
            return

        for sock in self.socks:
            if sock is not None:
                try:
                    sock.close()
                except Exception:
                    pass

        self.socks = [None] * PORT_N

        self.thread_lock.release()

    def _lock(self):

        if OS == 'Linux':
            so = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                addr = '\0/portlock/' + self.key
                so.bind(addr)
                self.socks[0] = so
                logger.debug('success to bind: {addr}'.format(addr=addr))
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    logger.debug('failure to bind: {addr}'.format(addr=addr))
                else:
                    raise

            return

        # other OS

        for i in range(len(self.socks)):

            addr = (self.addr[0], self.addr[1] + i)

            so = self._socket()

            try:
                so.bind(addr)
                self.socks[i] = so
                logger.debug('success to bind: {addr}'.format(addr=addr))
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    logger.debug('failure to bind: {addr}'.format(addr=addr))
                else:
                    raise

    def _socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, typ, value, traceback):
        self.release()

    def __del__(self):
        self.release()


def str_to_addr(x):

    # builtin hash() gives bad distribution with sequencial values.
    # re-hash it with 32 bit fibonacci hash.
    # And finally embed it into ip and port

    r = hashlib.sha1(str(x)).hexdigest()
    r = int(r, 16)
    p = r % (PORT_RANGE[1] - PORT_RANGE[0]) + PORT_RANGE[0]

    return ("127.0.0.1", p)


def test_collision():

    import resource
    resource.setrlimit(resource.RLIMIT_NOFILE, (102400, 102400))

    dd = {}
    ls = []
    for i in range(1 << 15):
        key = str(hashlib.sha1(str(i)).hexdigest())
        lck = key
        print 'lock is', i, lck
        l = Portlock(lck, timeout=8)
        r = l.try_lock()
        if not r:
            print 'collide', i, l.addr
            print l.socks

        dd[l.addr] = i
        ls.append(l)
