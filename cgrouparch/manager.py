import logging
import os
import time

import redis
from kazoo.client import KazooClient

from pykit import threadutil
from pykit import utfjson
from pykit.cgrouparch import account
from pykit.cgrouparch import cgroup_manager
from pykit.cgrouparch import communicate

logger = logging.getLogger(__name__)


global_value = {}


def init_redis_client(context):
    client = redis.StrictRedis(context['redis_ip'], context['redis_port'])
    context['redis_client'] = client


def get_zk_client(context):
    host = context['get_zk_host']()
    zk_client = KazooClient(hosts=host, timeout=3.0, randomize_hosts=True,
                            auth_data=context['zk_auth_data'], logger=logger)

    zk_client.start()

    return zk_client


def update_conf(event):
    logger.info('update conf triggered at: %f' % time.time())

    context = global_value['context']

    zk_path = '%s/arch_conf' % context['zk_prefix']

    while True:
        try:
            zk_client = context['zk_client']
            resp = zk_client.get(zk_path, watch=update_conf)
            break

        except Exception as e:
            logger.exception('failed to get from zk: ' + repr(e))
            time.sleep(5)

    context['arch_conf'] = {
        'version': resp[1].version,
        'value': utfjson.load(resp[0]),
    }

    logger.info('arch conf in zk changed at: %f, current verrsion: %d' %
                (time.time(), resp[1].version))

    cgroup_manager.build_all_subsystem_cgroup_arch(context)


def on_lost(stat):
    logger.warn('zk client on lost, stat is: %s, about to exit' % str(stat))
    os._exit(2)


def init_arch_conf(context):
    while True:
        try:
            if context['zk_client'] is None:
                context['zk_client'] = get_zk_client(context)
                context['zk_client'].add_listener(on_lost)

            zk_path = '%s/arch_conf' % context['zk_prefix']
            resp = context['zk_client'].get(zk_path, watch=update_conf)

            context['arch_conf'] = {
                'version': resp[1].version,
                'value': utfjson.load(resp[0]),
            }

            return

        except Exception as e:
            logger.warn('failed to get arch conf from zk: %s' % repr(e))

            try:
                context['zk_client'].stop()
            except Exception as e:
                logger.info('failed to stop zk client: ' + repr(e))

            context['zk_client'] = None
            time.sleep(10)


def update_cgexec_arg(cgexec_arg, subsystem_name, cgroup_relative_path,
                      cgroup_conf):
    sub_cgroup = cgroup_conf.get('sub_cgroup')
    if sub_cgroup is None:
        return

    for sub_cgroup_name, sub_cgroup_conf in sub_cgroup.iteritems():
        sub_relative_path = cgroup_relative_path + '/' + sub_cgroup_name

        if sub_cgroup_name in cgexec_arg:
            cgexec_arg[sub_cgroup_name] += ' -g %s:%s' % (
                subsystem_name, sub_relative_path)

        update_cgexec_arg(cgexec_arg, subsystem_name, sub_relative_path,
                          sub_cgroup_conf)


def get_cgexec_arg(cgroup_names, **argkv):
    context = {
        'cgroup_dir': argkv.get('cgroup_dir', '/sys/fs/cgroup'),
        'get_zk_host': argkv['get_zk_host'],
        'zk_prefix': argkv['zk_prefix'],
        'zk_auth_data': argkv['zk_auth_data'],
    }

    cgexec_arg = {}
    for cgroup_name in cgroup_names:
        cgexec_arg[cgroup_name] = ''

    try:
        zk_client = get_zk_client(context)

        zk_path = '%s/arch_conf' % context['zk_prefix']
        resp = zk_client.get(zk_path)

        zk_client.stop()

        context['arch_conf'] = {
            'version': resp[1].version,
            'value': utfjson.load(resp[0]),
        }
        cgroup_manager.build_all_subsystem_cgroup_arch(context)

        arch_conf_value = context['arch_conf']['value']
        for subsystem_name, subsystem_conf in arch_conf_value.iteritems():
            cgroup_relative_path = ''
            cgroup_conf = subsystem_conf
            update_cgexec_arg(cgexec_arg, subsystem_name,
                              cgroup_relative_path, cgroup_conf)

        return cgexec_arg

    except Exception as e:
        logger.exception('failed to get cgexec arg: ' + repr(e))
        return cgexec_arg


def run(**argkv):
    context = {
        'get_cgroup_pid_file': argkv['get_cgroup_pid_file'],
        'cgroup_dir': argkv.get('cgroup_dir', '/sys/fs/cgroup'),

        'communicate_ip': argkv.get('communicate_ip', '0.0.0.0'),
        'communicate_port': argkv.get('communicate_port', 43409),

        'tasks_update_interval': argkv.get('tasks_update_interval', 30),

        'redis_ip': argkv['redis_ip'],
        'redis_port': argkv['redis_port'],
        'redis_prefix': argkv.get('redis_prefix', 'cgroup_arch'),
        'redis_client': None,
        'redis_expire_time': argkv.get('redis_expire_time', 60 * 5),

        'get_zk_host': argkv['get_zk_host'],
        'zk_prefix': argkv['zk_prefix'],
        'zk_auth_data': argkv['zk_auth_data'],
        'zk_client': None,

        'protected_cgroup': argkv.get('protected_cgroup'),

        'arch_conf': None,
    }

    init_redis_client(context)
    init_arch_conf(context)

    global_value['context'] = context

    cgroup_manager.build_all_subsystem_cgroup_arch(context)

    cgroup_manager.set_cgroup(context)

    cgroup_manager.reset_statistics(context)

    threadutil.start_daemon_thread(account.run, args=(context,))

    threadutil.start_daemon_thread(cgroup_manager.loop_set_cgroup,
                                   args=(context,))

    communicate.run(context, ip=context['communicate_ip'],
                    port=context['communicate_port'])
