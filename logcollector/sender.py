import logging

logger = logging.getLogger(__name__)


def run(context):
    queue = context['queue']

    while True:
        log_entry = queue.get()

        try:
            context['send_log'](log_entry)
        except Exception as e:
            logger.exception('failed to send log entry: %s' % repr(e))
