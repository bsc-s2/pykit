import logging
import os
import threading
import time
from collections import defaultdict

import redis

from pykit import utfjson

logger = logging.getLogger(__name__)

# redis is thread safe

# NOTE: fork may duplicate file descriptor that confuses connection pool.
_pid_client = defaultdict(dict)
_lock = threading.RLock()


def get_client(ip_port):

    ip_port = normalize_ip_port(ip_port)

    pid = os.getpid()

    with _lock:
        o = _pid_client[ip_port]

        if pid not in o:
            o[pid] = redis.StrictRedis(*ip_port)

    return _pid_client[ip_port][pid]


def wait_serve(ip_port, timeout=5):

    t = time.time() + timeout

    rcl = get_client(ip_port)

    while time.time() < t:
        try:
            rcl.hget('foo', 'foo')
            logger.info('redis is ready: ' + repr(ip_port))
            return

        except redis.ConnectionError as e:
            logger.info('can not connect to redis: ' +
                        repr(ip_port) + ' ' + repr(e))
            time.sleep(0.1)
            continue
    else:
        logger.error('can not connect to redis: ' + repr(ip_port))
        raise


class RedisChannel(object):

    '''
    send message `data` through `channel`.
    `channel` is a list in redis.
    `peer` is "client" or "server".

    send is a rpush operation that adds an item to the end of a list.
    recv is a lpop operation that pops an item from the start of a list.
    '''

    other_peer = {
        'client': 'server',
        'server': 'client',
    }

    def __init__(self, ip_port, channel, peer, timeout=None):

        assert peer in self.other_peer

        self.ip_port = normalize_ip_port(ip_port)
        self.rcl = get_client(self.ip_port)

        # convert ['a', 'b'] to '/a/b'
        if isinstance(channel, (list, tuple)):
            channel = '/' + '/'.join(channel)

        self.channel = channel
        self.peer = peer.lower()
        self.send_list_name = '/'.join([self.channel, self.peer])
        self.recv_list_name = '/'.join([self.channel,
                                        self.other_peer[self.peer]])
        self.timeout = timeout

    def send_msg(self, data):
        j = utfjson.dump(data)
        self.rcl.rpush(self.send_list_name, j)

        if self.timeout is not None:
            self.rcl.expire(self.send_list_name, self.timeout)

    def recv_msg(self):

        v = self.rcl.lpop(self.recv_list_name)
        if v is None:
            return None

        return utfjson.load(v)

    def brecv_msg(self, timeout=0):

        v = self.rcl.blpop(self.recv_list_name, timeout=timeout)
        if v is None or len(v) != 2:
            return None

        # v is a tuple, (key, value)
        _, value = v

        return utfjson.load(value)

    def recv_last_msg(self):

        last = None
        while True:
            v = self.rcl.lpop(self.recv_list_name)
            if v is None:
                return utfjson.load(last)

            last = v

    def brecv_last_msg(self, timeout=0):

        msg = self.brecv_msg(timeout=timeout)
        if msg is None:
            return None

        last = self.recv_last_msg() or msg

        return last

    def peek_msg(self):
        v = self.rcl.lindex(self.recv_list_name, 0)
        if v is None:
            return None

        return utfjson.load(v)

    def rpeek_msg(self):
        v = self.rcl.lindex(self.recv_list_name, -1)
        if v is None:
            return None

        return utfjson.load(v)

    def list_channel(self, prefix):
        if isinstance(prefix, (list, tuple)):
            _prefix = '/' + '/'.join(prefix) + '/'
        else:
            _prefix = prefix

        if not _prefix.startswith('/'):
            raise ValueError(
                'prefix must starts with "/", but:' + repr(prefix))

        if _prefix.endswith('*'):
            raise ValueError(
                'prefix must NOT ends with "*", but:' + repr(prefix))

        if not _prefix.endswith('/'):
            raise ValueError('prefix must ends with "/", but:' + repr(prefix))

        _prefix = _prefix + '*'
        channels = self.rcl.keys(_prefix)

        rst = []
        for c in channels:

            for k in self.other_peer:
                k = '/' + k
                if c.endswith(k):
                    c = c[:-len(k)]
                    break
            else:
                logger.info('not a channel: ' + repr(c))
                continue

            if c not in rst:
                rst.append(c)

        return sorted(rst)


def normalize_ip_port(ip_port):
    if isinstance(ip_port, (int, long)):
        ip_port = ('127.0.0.1', ip_port)

    return ip_port
