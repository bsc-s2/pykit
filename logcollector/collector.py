import logging
import Queue
import threading
import time
from datetime import datetime

from pykit import threadutil
from pykit.logcollector import cache_flusher
from pykit.logcollector import scanner
from pykit.logcollector import sender

logger = logging.getLogger(__name__)


def run(**kwargs):
    context = {
        'node_id': kwargs['node_id'],
        'node_ip': kwargs['node_ip'],
        'send_log': kwargs['send_log'],

        'conf': kwargs['conf'],

        'cache_lock': threading.RLock(),

        'cache': {},
        'stat': {},

        'queue': Queue.Queue(1024 * 10),
    }

    # strptime not thread safe, need to call it manually before
    # initiating any thread
    datetime.strptime("2011-04-05", "%Y-%m-%d")

    for log_name in context['conf'].keys():
        context['cache'][log_name] = {}
        context['stat'][log_name] = {}

        threadutil.start_daemon_thread(
            scanner.scan,
            args=(context, log_name))

    threadutil.start_daemon_thread(cache_flusher.run, args=(context,))

    threadutil.start_daemon_thread(sender.run, args=(context,))

    while True:
        # actually it is not an error log, but normally we only report
        # error log, and we want to report this log even it is not
        # an error log.
        logger.error('stat: %s' % context['stat'])

        time.sleep(100)
