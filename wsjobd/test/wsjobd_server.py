#!/usr/bin/env python2
# coding: utf-8
import logging
from collections import OrderedDict

from geventwebsocket import Resource
from geventwebsocket import WebSocketServer

from pykit import wsjobd

PORT = 33445


def run():
    WebSocketServer(
        ('127.0.0.1', PORT),
        Resource(OrderedDict({'/': wsjobd.JobdWebSocketApplication})),
    ).serve_forever()


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler('wsjobd.log')
    formatter = logging.Formatter('[%(asctime)s, %(levelname)s] %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    from pykit import daemonize
    daemonize.daemonize_cli(run, '/tmp/wsjod_server.pid')
