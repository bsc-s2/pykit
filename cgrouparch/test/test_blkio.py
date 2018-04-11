#!/usr/bin/env python2
# coding: utf-8

import mmap
import multiprocessing
import os
import random
import time
import unittest

from pykit import fsutil
from pykit import ututil
from pykit.cgrouparch import cgroup_manager
from pykit.cgrouparch import cgroup_util

dd = ututil.dd

random.seed(time.time())

base_dir = os.path.dirname(__file__)


class TestBlkio(unittest.TestCase):

    def worker(self, index, duration, result_dict):
        # wait for the cgroup directory tree to be setup.
        time.sleep(0.2)

        m = mmap.mmap(-1, 1024 * 1024 * 2)
        data = ' ' * 1024 * 1024 * 2
        m.write(data)

        file_path = os.path.join(base_dir, 'test_file_%d' % index)
        f = os.open(file_path, os.O_CREAT |
                    os.O_DIRECT | os.O_TRUNC | os.O_RDWR)

        start_time = time.time()
        dd('worker %d %d started at: %f' %
           (index, os.getpid(), start_time))

        count = 0
        while True:
            os.write(f, m)
            count += 1
            dd('worker %d %d wrote %d times' %
               (index, os.getpid(), count))

            if time.time() - start_time > duration:
                break

        dd('worker %d %d stoped at: %f' %
           (index, os.getpid(), time.time()))

        result_dict[index] = count

        os.close(f)
        return

    def test_blkio_weight(self):
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

        p4 = multiprocessing.Process(target=self.worker,
                                     args=(4, 10, result_dict))
        p4.daemon = True
        p4.start()

        arch_conf = {
            'blkio': {
                'sub_cgroup': {
                    'test_cgroup_a': {
                        'conf': {
                            'weight': int(500 * 0.95),
                        },
                        'sub_cgroup': {
                            'test_cgroup_a_sub1': {
                                'conf': {
                                    'weight': 500,
                                    'pids': [p1.pid],
                                },
                            },
                            'test_cgroup_a_sub2': {
                                'conf': {
                                    'weight': 500,
                                    'pids': [p2.pid],
                                },
                            },
                        },
                    },
                    'test_cgroup_b': {
                        'conf': {
                            'weight': int(500 * 0.05),
                        },
                        'sub_cgroup': {
                            'test_cgroup_b_sub1': {
                                'conf': {
                                    'weight': 500,
                                    'pids': [p3.pid],
                                },
                            },
                            'test_cgroup_b_sub2': {
                                'conf': {
                                    'weight': 500,
                                    'pids': [p4.pid],
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
        p4.join()

        for cgrou_name in arch_conf['blkio']['sub_cgroup'].keys():
            cgroup_util.remove_cgroup(
                os.path.join(context['cgroup_dir'], 'blkio'),
                os.path.join(context['cgroup_dir'], 'blkio', cgrou_name))

        for i in range(1, 5):
            fsutil.remove(os.path.join(base_dir, 'test_file_%d' % i))

        dd(result_dict)

        self.assertGreater(result_dict[1] + result_dict[2],
                           result_dict[3] + result_dict[4])
