
import errno
import hashlib
import socket
import time

port_n = 3
port_range = (40000, 60000)

default_sleep_time = 0.01  # sec


class PortlockError(Exception):
    pass


class PortlockTimeout(PortlockError):
    pass


class Portlock(object):

    def __init__(self, key, timeout=1, sleep_time=None):

        self.key = key
        self.addr = str_to_addr(key)
        self.timeout = timeout
        self.sleep_time = sleep_time or default_sleep_time
        self.socks = [None] * port_n

    def try_lock(self):

        self._lock()

        if self.has_locked():
            return True
        else:
            self.socks = [None] * port_n
            return False

    def has_locked(self):

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

        for sock in self.socks:
            if sock is not None:
                sock.close()

        self.socks = [None] * port_n

    def _lock(self):

        for i in range(len(self.socks)):

            addr = (self.addr[0], self.addr[1] + i)

            so = self._socket()

            try:
                so.bind(addr)
                self.socks[i] = so
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    pass
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
    p = r % (port_range[1] - port_range[0]) + port_range[0]

    return ("127.0.0.1", p)


if __name__ == "__main__":

    import resource
    resource.setrlimit(resource.RLIMIT_NOFILE, (10240, -1))

    def test_collision():
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

    test_collision()
