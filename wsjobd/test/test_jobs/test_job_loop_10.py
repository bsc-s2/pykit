#!/usr/bin/env python2
# coding: utf-8

import logging
import time

logger = logging.getLogger(__name__)


def run(job):

    data = job.data

    for i in range(10):
        data['n'] = i
        time.sleep(1)
