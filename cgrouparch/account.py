import logging
import os
import time

from pykit import utfjson
from pykit.cgrouparch import model

logger = logging.getLogger(__name__)


def account_one_cgroup(slot_number, subsystem_model, cgroup_path,
                       cgroup_conf, result):
    account_value = subsystem_model['account'](cgroup_path)
    result['value'] = account_value

    sub_cgroup = cgroup_conf.get('sub_cgroup')
    if sub_cgroup is None:
        return

    result['sub_cgroup'] = {}

    for sub_cgroup_name, sub_cgroup_conf in sub_cgroup.iteritems():
        sub_cgroup_path = os.path.join(cgroup_path, sub_cgroup_name)

        result['sub_cgroup'][sub_cgroup_name] = {}

        account_one_cgroup(slot_number, subsystem_model, sub_cgroup_path,
                           sub_cgroup_conf,
                           result['sub_cgroup'][sub_cgroup_name])


def _run(context, slot_number):
    arch_conf = context['arch_conf']['value']

    result = {}

    for subsystem_name, subsystem_arch_conf in arch_conf.iteritems():
        subsystem_model = model.subsystem[subsystem_name]

        cgroup_path = os.path.join(context['cgroup_dir'], subsystem_name)
        cgroup_conf = subsystem_arch_conf

        result[subsystem_name] = {}

        account_one_cgroup(slot_number, subsystem_model, cgroup_path,
                           cgroup_conf, result[subsystem_name])

    redis_client = context['redis_client']

    key_name = '%s/account/%d' % (context['redis_prefix'], slot_number)

    redis_client.set(key_name, utfjson.dump(result))
    redis_client.expire(key_name, context['redis_expire_time'])


def run(context):
    while True:
        try:
            start_ts = time.time()
            slot_number = int(round(start_ts))

            _run(context, slot_number)

            end_ts = time.time()

            logger.info('account at: %f, time used: %f' %
                        (start_ts, end_ts - start_ts))

            to_sleep = slot_number + 1 - end_ts
            if to_sleep <= 0:
                logger.error('account use too much time')
                to_sleep = 0.1

            time.sleep(to_sleep)

        except Exception as e:
            logger.exception('failed to account: %s' % repr(e))
            time.sleep(1)


def show(context, args):
    end_slot = args.get('end_slot', int(time.time()))
    nr_slot = args.get('nr_slot', 10)

    start_slot = args.get('start_slot', end_slot - nr_slot + 1)

    result = {}

    redis_client = context['redis_client']

    for slot_number in range(start_slot, end_slot + 1):
        key_name = '%s/account/%d' % (context['redis_prefix'], slot_number)

        value_str = redis_client.get(key_name)
        if value_str is None:
            continue

        result[slot_number] = utfjson.load(value_str)

    return result
