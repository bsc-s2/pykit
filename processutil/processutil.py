#!/usr/bin/env python2
# coding: utf-8

import logging
import os

from pykit import daemonize

logger = logging.getLogger(__name__)


def start_exec_process(cmd, target, *args):

    def _run():
        try:
            os.execlp(cmd, cmd, target, *args)
        except OSError:
            pass

    try:
        pid = os.fork()
        if pid == 0:
            d = daemonize.Daemon('')
            d.daemonize()
            _run()
        else:
            os.wait()
    except OSError as e:
        logger.error("fork failed: " + repr(e))
        raise
