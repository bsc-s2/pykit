import logging
import os

from pykit import fsutil

logger = logging.getLogger(__name__)


def create_cgroup(cgroup_path):
    os.mkdir(cgroup_path, 0755)
    return


def add_pids(cgroup_path, pids):
    task_file = os.path.join(cgroup_path, 'tasks')

    for pid in pids:
        try:
            fsutil.write_file(task_file, str(pid), fsync=False)
        except Exception as e:
            logger.info('failed to add pid: %s to file: %s, %s' %
                        (str(pid), task_file, repr(e)))
    return


def clear_pids(subsystem_dir, cgroup_path):
    task_file = os.path.join(cgroup_path, 'tasks')
    f = open(task_file, 'r')

    while True:
        line = f.readline()
        if line == '':
            break

        pid = line.strip()

        add_pids(subsystem_dir, [pid])

    return


def remove_cgroup(subsystem_dir, cgroup_path):
    sub_dirs = fsutil.get_sub_dirs(cgroup_path)

    for sub_dir in sub_dirs:
        sub_cgroup_path = os.path.join(cgroup_path, sub_dir)
        remove_cgroup(subsystem_dir, sub_cgroup_path)

    clear_pids(subsystem_dir, cgroup_path)
    os.rmdir(cgroup_path)

    return
