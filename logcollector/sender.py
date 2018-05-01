import logging

logger = logging.getLogger(__name__)


def run(context):
    queue = context['queue']

    while True:
        log_entry = queue.get()

        try:
            context['send_log'](log_entry)
        except Exception:
            # do not log repr(e), it may cause endless escape of '\'.
            logger.error('failed to send log entry')
