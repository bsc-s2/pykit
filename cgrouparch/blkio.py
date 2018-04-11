import logging
import os

from pykit import fsutil
from pykit.cgrouparch import cgroup_util

logger = logging.getLogger(__name__)


def set_cgroup(cgroup_path, conf):
    if 'weight' in conf:
        weight_file = os.path.join(cgroup_path, 'blkio.weight')

        weight = str(conf['weight'])

        fsutil.write_file(weight_file, weight, fsync=False)
        logger.info('write: %s to file: %s' % (weight, weight_file))

    pids = conf.get('pids')

    if pids is None:
        return

    cgroup_util.add_pids(cgroup_path, pids)
    logger.info('add pids: %s to cgroup: %s' % (repr(pids), cgroup_path))


def reset_statistics(cgroup_path):
    reset_file = os.path.join(cgroup_path, 'blkio.reset_stats')
    fsutil.write_file(reset_file, '1', fsync=False)


def account(cgroup_path):
    file_name = os.path.join(cgroup_path, 'blkio.io_service_bytes_recursive')

    # file content format:
    # 8:0 Read 1053712384
    # 8:0 Write 81929383424
    # 8:0 Sync 80865775616
    # 8:0 Async 2117320192
    # 8:0 Total 82983095808
    # 8:16 Read 1053712384
    # 8:16 Write 81929383424
    # ...
    # Total 82983095808

    content = fsutil.read_file(file_name)
    lines = content.split('\n')[:-1]

    r = {}
    for line in lines:
        parts = line.split()
        if parts[1] in ('Read', 'Write'):
            r[parts[0]] = r.get(parts[0]) or {}
            r[parts[0]][parts[1]] = int(parts[2])

    return r
