import logging
import time

logger = logging.getLogger(__name__)


def enqueue_log_entry(ts_cache, queue):
    # ts_cache = {
    #     'source_file_xxx': {
    #         123: {  # 123 is line number
    #             ...
    #         },
    #         ...
    #     },
    #     ...
    # }
    for _, source_file_cache in ts_cache.iteritems():
        for _, log_entry in source_file_cache.iteritems():
            queue.put(log_entry)


def flush_cache(log_cache, queue):
    ts_list = log_cache.keys()

    if len(ts_list) == 0:
        return

    ts_list.sort()

    # keep the latest log if it is generated in about 2 second.
    if time.time() - ts_list[-1] < 2:
        ts_list = ts_list[:-1]

    # only enqueue logs of latest 3 ts.
    for log_ts in ts_list[-3:]:
        enqueue_log_entry(log_cache[log_ts], queue)

    for log_ts in ts_list:
        del log_cache[log_ts]


def one_flush(context):

    for log_name in context['cache'].keys():
        log_cache = context['cache'][log_name]
        log_stat = context['stat'][log_name]

        try:
            flush_cache(log_cache, context['queue'])
            log_stat['flush_cache_error'] = None

        except Exception as e:
            logger.exception('failed to flush cache of: %s, %s' %
                             (log_name, repr(e)))
            log_stat['flush_cache_error'] = repr(e)


def run(context):
    while True:
        start_time = time.time()

        with context['cache_lock']:
            one_flush(context)

        time_used = time.time() - start_time

        logger.info('flush at: %f, time used: %f' %
                    (start_time, time_used))

        time.sleep(1)
