import logging
import os
import time

from pykit import fsutil
from pykit.cgrouparch import cgroup_util
from pykit.cgrouparch import model
from pykit.cgrouparch import util

logger = logging.getLogger(__name__)


def get_pids_of_one_pid_file(pid_file):
    try:
        pid = util.get_pid_from_file(pid_file)
        pids = util.get_all_pids(pid)
        logger.info('pids for pid file: %s is %s' % (pid_file, pids))
        return pids

    except Exception as e:
        logger.exception('failed to get pids of pid file: %s, %s' %
                         (pid_file, repr(e)))
        return []


def get_cgroup_pids(pid_files):
    cgroup_pids = []

    for pid_file in pid_files:
        pids = get_pids_of_one_pid_file(pid_file)
        cgroup_pids.extend(pids)

    return cgroup_pids


def update_one_cgroup_pids(cgroup_path, cgroup_conf, context):
    if 'conf' in cgroup_conf:
        cgroup_name = os.path.split(cgroup_path)[-1]
        try:
            pid_files = context['get_cgroup_pid_file'](cgroup_name)
            if pid_files is not None:
                cgroup_conf['conf']['pids'] = get_cgroup_pids(pid_files)

        except Exception as e:
            logger.exception('failed to get pid files of: %s, %s' %
                             (cgroup_name, repr(e)))

    sub_cgroup = cgroup_conf.get('sub_cgroup')
    if sub_cgroup is None:
        return

    for sub_cgroup_name, sub_cgroup_conf in sub_cgroup.iteritems():
        sub_cgroup_path = os.path.join(cgroup_path, sub_cgroup_name)

        update_one_cgroup_pids(sub_cgroup_path, sub_cgroup_conf, context)

    return


def update_cgroup_pids(context):
    arch_conf = context['arch_conf']['value']

    for subsystem_name, subsystem_arch_conf in arch_conf.iteritems():
        cgroup_path = os.path.join(context['cgroup_dir'], subsystem_name)
        cgroup_conf = subsystem_arch_conf

        try:
            update_one_cgroup_pids(cgroup_path, cgroup_conf, context)
        except Exception as e:
            logger.exception('failed to update pids of cgroup: %s, %s' %
                             (cgroup_path, repr(e)))
    return


def build_cgroup_arch(subsystem_dir, cgroup_path, cgroup_conf,
                      protected_cgroup):
    sub_dirs = fsutil.get_sub_dirs(cgroup_path)

    sub_cgroup = cgroup_conf.get('sub_cgroup', {})

    for sub_dir in sub_dirs:
        if sub_dir not in sub_cgroup:
            path = os.path.join(cgroup_path, sub_dir)
            logger.warn('unknown cgroup: %s' % path)

            if sub_dir in protected_cgroup:
                continue

            cgroup_util.remove_cgroup(subsystem_dir, path)
            logger.info('remove unknown cgroup: %s', path)

    for sub_cgroup_name, sub_cgroup_conf in sub_cgroup.iteritems():
        sub_cgroup_path = os.path.join(cgroup_path, sub_cgroup_name)

        if sub_cgroup_name not in sub_dirs:
            cgroup_util.create_cgroup(sub_cgroup_path)
            logger.info('create cgroup: %s', sub_cgroup_path)

        build_cgroup_arch(subsystem_dir, sub_cgroup_path,
                          sub_cgroup_conf, protected_cgroup)

    return


def build_all_subsystem_cgroup_arch(context):
    arch_conf = context['arch_conf']['value']

    for subsystem_name, subsystem_arch_conf in arch_conf.iteritems():
        subsystem_dir = os.path.join(context['cgroup_dir'], subsystem_name)

        cgroup_path = subsystem_dir
        cgroup_conf = subsystem_arch_conf

        protected_cgroup = context.get('protected_cgroup')
        if protected_cgroup is None:
            protected_cgroup = []

        build_cgroup_arch(subsystem_dir, cgroup_path, cgroup_conf,
                          protected_cgroup)


def set_one_cgroup(subsystem_model, cgroup_path, cgroup_conf):
    if 'conf' in cgroup_conf:
        subsystem_model['set_cgroup'](cgroup_path, cgroup_conf['conf'])

    sub_cgroup = cgroup_conf.get('sub_cgroup')
    if sub_cgroup is None:
        return

    for sub_cgroup_name, sub_cgroup_conf in sub_cgroup.iteritems():
        sub_cgroup_path = os.path.join(cgroup_path, sub_cgroup_name)

        set_one_cgroup(subsystem_model, sub_cgroup_path, sub_cgroup_conf)

    return


def set_cgroup(context):
    update_cgroup_pids(context)

    arch_conf = context['arch_conf']['value']

    for subsystem_name, subsystem_arch_conf in arch_conf.iteritems():
        cgroup_path = os.path.join(context['cgroup_dir'], subsystem_name)
        cgroup_conf = subsystem_arch_conf

        subsystem_model = model.subsystem[subsystem_name]

        try:
            set_one_cgroup(subsystem_model, cgroup_path, cgroup_conf)
        except Exception as e:
            logger.exception('failed to set cgroup: %s, %s' %
                             (cgroup_path, repr(e)))
    return


def loop_set_cgroup(context):
    while True:
        start_time = time.time()

        set_cgroup(context)

        time_used = time.time() - start_time
        logger.info('set cgroup at: %f, time used: %f' %
                    (start_time, time_used))

        time.sleep(context['tasks_update_interval'])


def reset_statistics_one_cgroup(subsystem_model, cgroup_path, cgroup_conf):
    subsystem_model['reset_statistics'](cgroup_path)
    logger.info('reset statistics of cgroup: %s' % cgroup_path)

    sub_cgroup = cgroup_conf.get('sub_cgroup')
    if sub_cgroup is None:
        return

    for sub_cgroup_name, sub_cgroup_conf in sub_cgroup.iteritems():
        sub_cgroup_path = os.path.join(cgroup_path, sub_cgroup_name)

        reset_statistics_one_cgroup(subsystem_model, sub_cgroup_path,
                                    sub_cgroup_conf)
    return


def reset_statistics(context):
    arch_conf = context['arch_conf']['value']

    for subsystem_name, subsystem_arch_conf in arch_conf.iteritems():
        cgroup_path = os.path.join(context['cgroup_dir'], subsystem_name)
        cgroup_conf = subsystem_arch_conf

        subsystem_model = model.subsystem[subsystem_name]

        try:
            reset_statistics_one_cgroup(subsystem_model, cgroup_path,
                                        cgroup_conf)
        except Exception as e:
            logger.exception('failed to reset statistics of cgroup: %s, %s' %
                             (cgroup_path, repr(e)))
    return
