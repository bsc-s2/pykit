#!/usr/bin/env python2
# coding: utf-8

import logging
from collections import OrderedDict

from geventwebsocket import Resource
from geventwebsocket import WebSocketApplication
from geventwebsocket import WebSocketServer

from pykit import utfjson
from pykit.cgrouparch import account

global_value = {}

logger = logging.getLogger(__name__)


class CgroupArchWebSocketApplication(WebSocketApplication):

    def on_open(self):
        logger.info('on open')

    def on_message(self, message_str):
        if message_str is None:
            return

        try:
            self.process_message(message_str)
        except Exception as(e):
            logger.exception('failed to process message: ' + repr(e))
            self.send_json({'error': repr(e)})

    def on_close(self, reason):
        logger.info('on close')

    def process_message(self, message_str):
        message = utfjson.load(message_str)

        cmd = message['cmd']
        args = message.get('args')
        if args is None:
            args = {}

        result = self.do_cmd(cmd, args)
        self.send_json(result)

    def do_cmd(self, cmd, args):
        if cmd == 'show_account':
            return self.show_account(args)
        elif cmd == 'get_conf':
            return global_value['context']['arch_conf']
        else:
            return {'error': 'invalid cmd: %s' % cmd}

    def show_account(self, args):
        return account.show(global_value['context'], args)

    def send_json(self, value):
        value_str = utfjson.dump(value)
        self.ws.send(value_str)


def run(context, ip='0.0.0.0', port=22348):
    global_value['context'] = context
    WebSocketServer(
        (ip, port),
        Resource(OrderedDict({'/': CgroupArchWebSocketApplication})),
    ).serve_forever()
