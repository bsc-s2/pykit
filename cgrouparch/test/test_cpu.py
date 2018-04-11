#!/usr/bin/env python2
# coding: utf-8

import multiprocessing
import os
import random
import time
import unittest

from pykit import ututil
from pykit.cgrouparch import cgroup_manager
from pykit.cgrouparch import cgroup_util

dd = ututil.dd

random.seed(time.time())


class TestCpu(unittest.TestCase):

    def compute_work(self):
        i = 0
        while True:
            i += 1
            if i > 1024 * 1024:
                break

    def worker(self, index, duration, result_dict):
        # wait for the cgroup directory tree to be setup.
        time.sleep(0.2)

        start_time = time.time()
        dd('worker %d %d started at: %f' %
           (index, os.getpid(), start_time))

        count = 0
        while True:
            self.compute_work()
            count += 1
            dd('worker %d %d computed %d times' %
               (index, os.getpid(), count))

            if time.time() - start_time > duration:
                break

        dd('worker %d %d stoped at: %f' %
           (index, os.getpid(), time.time()))

        result_dict[index] = count
        return

    def test_cpu_share(self):
        manager = multiprocessing.Manager()
        result_dict = manager.dict()

        p1 = multiprocessing.Process(target=self.worker,
                                     args=(1, 10, result_dict))
        p1.daemon = True
        p1.start()

        p2 = multiprocessing.Process(target=self.worker,
                                     args=(2, 10, result_dict))
        p2.daemon = True
        p2.start()

        p3 = multiprocessing.Process(target=self.worker,
                                     args=(3, 10, result_dict))
        p3.daemon = True
        p3.start()

        arch_conf = {
            'cpu': {
                'sub_cgroup': {
                    'test_cgroup_a': {
                        'conf': {
                            'share': 500,
                            'pids': [p1.pid],
                        },
                    },
                    'test_cgroup_b': {
                        'conf': {
                            'share': 1000,
                        },
                        'sub_cgroup': {
                            'test_cgroup_b_sub1': {
                                'conf': {
                                    'share': 100,
                                    'pids': [p2.pid],
                                },
                            },
                            'test_cgroup_b_sub2': {
                                'conf': {
                                    'share': 300,
                                    'pids': [p3.pid],
                                },
                            },
                        },
                    },
                },
            },
        }

        context = {
            'cgroup_dir': '/sys/fs/cgroup',
            'arch_conf': {
                'value': arch_conf
            },
        }

        cgroup_manager.build_all_subsystem_cgroup_arch(context)
        cgroup_manager.set_cgroup(context)

        p1.join()
        p2.join()
        p3.join()

        dd(result_dict)

        for cgrou_name in arch_conf['cpu']['sub_cgroup'].keys():
            cgroup_util.remove_cgroup(
                os.path.join(context['cgroup_dir'], 'cpu'),
                os.path.join(context['cgroup_dir'], 'cpu', cgrou_name))

        level1_rate = float(result_dict[2] + result_dict[3]) / result_dict[1]
        dd(level1_rate)

        self.assertAlmostEqual(2.0, level1_rate, delta=0.2)

        level2_rate = float(result_dict[3]) / result_dict[2]
        dd(level2_rate)

        self.assertAlmostEqual(3.0, level2_rate, delta=0.5)
