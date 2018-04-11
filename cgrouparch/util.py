import logging

import psutil

from pykit import fsutil

logger = logging.getLogger(__name__)


def get_pid_from_file(pid_file):
    data = fsutil.read_file(pid_file)
    return int(data)


def get_all_pids(pid):
    all_pids = []

    try:
        process = psutil.Process(pid)

    except psutil.NoSuchProcess as e:
        logger.info('process %d does not exist' % pid)
        return all_pids

    except Exception as e:
        logger.exception('faild to get process of pid: %d, %s' %
                         (pid, repr(e)))
        return all_pids

    all_pids.append(process.pid)

    children = process.children(recursive=True)
    for process in children:
        all_pids.append(process.pid)

    return all_pids
