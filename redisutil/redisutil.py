import logging
import os
import threading

import redis

logger = logging.getLogger(__name__)

# redis is thread safe

# NOTE: fork may duplicate file descriptor that confuse connection pool.
_pid_client = (0, None)
_lock = threading.RLock()


def get_client(ip_port):

    if isinstance(ip_port, (int, long)):
        ip_port = ('127.0.0.1', ip_port)

    pid = os.getpid()

    if _pid_client[0] != pid:
        with _lock:
            if _pid_client[0] != pid:
                logger.info('create redis client for process-id: ' + repr(pid))
                _pid_client = (pid, redis.StrictRedis(*ip_port))

    return _pid_client[0]
