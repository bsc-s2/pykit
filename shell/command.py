#!/usr/bin/env python2
# coding: utf-8

import argparse
import copy
import sys
import logging
import os

from pykit import dictutil


logger = logging.getLogger(__name__)

def command(**kwargs):

    root, parser = add_command_help(kwargs)

    inputs = sys.argv[1:]

    try:
        cmds = []
        while len(inputs) > 0 and root.has_key(inputs[0]):

            k = inputs.pop(0)
            cmds.append(k)
            node = root[k]

            if is_node_executable(node):

                call_able, args = parse_executable_node(parser, cmds, node, inputs)

                try:
                    logger.debug("command: " + repr(cmds) + ' args: ' + repr(args) + ' cwd: ' + repr(os.getcwd()))

                    rc = call_able(*args)
                    sys.exit(0
                              if rc is True or rc is 0 or rc is None
                              else 1)

                except Exception as e:
                    logger.exception(repr(e))
                    sys.stderr.write(repr(e))
                    sys.exit(1)

            else:
                root = node

        if need_to_show_help(parser):

            if len(cmds) > 0:
                argv = [' '.join(cmds)] + inputs
            else:
                argv = inputs

            parser.parse_args(argv)
        else:
            sys.stderr.write('No such command: ' + ' '.join(sys.argv[1:]))

        sys.exit(2)

    except Exception as e:
        logger.exception(repr(e))
        sys.stderr.write(repr(e))
        sys.exit(1)


def add_command_help(commands):

    new_cmds = copy.deepcopy(commands)

    help_msgs = new_cmds.get('__add_help__')
    desc = new_cmds.get('__description__')

    for k in ('__add_help__', '__description__'):
        if new_cmds.has_key(k):
            del new_cmds[k]

    if help_msgs is None:
        return new_cmds, None

    parser = argparse.ArgumentParser(description=desc, epilog='\n')

    subparsers = parser.add_subparsers(help=' command(s) to select ...')

    for cmds, execute_able in dictutil.depth_iter(new_cmds):

        help = help_msgs.get(tuple(cmds), '')
        cmd = ' '.join(cmds)

        cmd_parser = subparsers.add_parser(cmd, help=help)

        if need_param_help(execute_able):
            call_able = execute_able[0]
            param_msgs = execute_able[1:]

            params = add_param_help(cmd_parser, param_msgs)

            # delete help message
            dictutil.make_setter(cmds)(new_cmds, (call_able, params))

    return new_cmds, parser


def add_param_help(parser, param_msgs):

    params = []
    for param, msg in param_msgs:
        parser.add_argument(param, **msg)
        params.append(param)

    return params


def parse_executable_node(parser, cmds, execute_able, args):

    if not need_to_show_help(parser):

        # no __add_help__ but has paramter help message
        if args_need_to_parse(execute_able):
            return execute_able[0], args

        return execute_able, args

    args_parsed = parser.parse_args([' '.join(cmds)] + args)
    # to dict
    args_parsed = vars(args_parsed)

    if not args_need_to_parse(execute_able):
        return execute_able, args

    call_able, params = execute_able

    args = [args_parsed.get(x) for x in params]

    return call_able, args


def is_node_executable(node):

    if isinstance(node, (list, tuple)) and len(node) > 0:
        return callable(node[0])

    return callable(node)


def need_to_show_help(parser):

    return parser is not None


def args_need_to_parse(execute_able):

    return isinstance(execute_able, tuple)


def need_param_help(execute_able):

    return isinstance(execute_able, (list, tuple)) and len(execute_able) > 1
