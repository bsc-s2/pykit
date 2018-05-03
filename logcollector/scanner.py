import logging
import os
import time

from pykit import fsutil

logger = logging.getLogger(__name__)


class ParseLogError(Exception):
    pass


def build_entry(context, log_name, file_name, log_str, log_conf):
    log_entry = {
        'log_name': log_name,
        'log_file': file_name,
        'content': log_str,
        'node_id': context['node_id'],
        'node_ip': context['node_ip'],
        'count': 1,
    }

    try:
        log_info = log_conf['parse'](log_str)

    except Exception as e:
        logger.exception('failed to parse log: %s, %s, %s' %
                         (log_name, log_str, repr(e)))
        raise ParseLogError('faild to parse log: %s' % log_name)

    log_entry.update(log_info)

    return log_entry


def put_into_cache(log_cache, log_entry):
    log_ts = log_entry['log_ts']
    source_file = log_entry['source_file']
    line_number = log_entry['line_number']

    if log_ts not in log_cache:
        log_cache[log_ts] = {}

    if source_file not in log_cache[log_ts]:
        log_cache[log_ts][source_file] = {}

    cache_source_file = log_cache[log_ts][source_file]

    if line_number not in cache_source_file:
        cache_source_file[line_number] = log_entry
        return

    old_entry = cache_source_file[line_number]

    log_entry['count'] = old_entry['count'] + 1

    cache_source_file[line_number] = log_entry
    return


def _iter_log(log_conf):
    file_path = log_conf['file_path']
    log_lines = []

    try:
        for line in fsutil.Cat(file_path).iterate(
                timeout=3, default_seek=-1024*1024*2):
            if log_conf['is_first_line'](line):
                if len(log_lines) > 0:
                    yield ''.join(log_lines)
                    log_lines = []

                log_lines = [line]
            else:
                if len(log_lines) < 100:
                    log_lines.append(line)

    except Exception as e:
        logger.info('got exception: %s when iter lines of file: %s' %
                    (repr(e), file_path))

        if len(log_lines) > 0:
            yield ''.join(log_lines)


def iter_log(log_conf):

    while True:
        for log_str in _iter_log(log_conf):
            yield log_str

        time.sleep(1)


def _scan(context, log_name):
    log_stat = context['stat'][log_name]
    log_conf = context['conf'][log_name]
    log_cache = context['cache'][log_name]

    file_path = log_conf['file_path']
    file_name = os.path.basename(file_path)

    log_stat['total_n'] = 0
    log_stat['reported_n'] = 0

    for log_str in iter_log(log_conf):
        log_str = log_str[:1024]
        log_stat['total_n'] += 1

        log_level = log_conf['get_level'](log_str)

        if log_level not in log_conf['level']:
            continue

        log_entry = build_entry(context, log_name, file_name,
                                log_str, log_conf)

        log_stat['latence'] = time.time() - log_entry['log_ts']

        log_stat['reported_n'] += 1

        with context['cache_lock']:
            put_into_cache(log_cache, log_entry)


def scan(context, log_name):
    while True:
        try:
            _scan(context, log_name)

        except Exception as e:
            logger.exception('failed to scan log: %s, %s' %
                             (log_name, repr(e)))

            context['stat'][log_name]['error'] = repr(e)
            time.sleep(1)
