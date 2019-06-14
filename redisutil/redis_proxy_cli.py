#!/usr/bin/env python2
# coding: utf-8

import logging
import socket

from pykit import awssign
from pykit import config
from pykit import http
from pykit import utfjson

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 2


class RedisProxyError(Exception):
    pass


class SendRequestError(RedisProxyError):
    pass


class KeyNotFoundError(RedisProxyError):
    pass


class ServerResponseError(RedisProxyError):
    pass


def _proxy(func):

    def _wrapper(self, verb, retry, *args):
        all_hosts = [self.hosts]
        if self.proxy_hosts is not None:
            all_hosts += self.proxy_hosts

        rst = None
        if verb == "GET":
            for hosts in all_hosts:
                try:
                    return func(self, hosts, verb, retry, *args)
                except RedisProxyError as e:
                    continue
            else:
                raise e

        else:
            for hosts in all_hosts:
                rst = func(self, hosts, verb, retry, *args)

        return rst

    return _wrapper


def _retry(func):

    def _wrapper(self, hosts, verb, retry, *args):
        retry = retry or 0

        for _ in range(retry + 1):
            for ip, port in hosts:
                self.ip = ip
                self.port = port

                try:
                    return func(self, verb, *args)

                except (http.HttpError, socket.error) as e:
                    logger.exception('{e} while send request to redis proxy with {ip}:{p}'.format(
                        e=repr(e), ip=ip, p=port))

        else:
            raise SendRequestError(repr(e))

    return _wrapper


class SetAPI(object):

    def __init__(self, cli, redis_op, mtd_info):
        self.cli = cli
        self.redis_op = redis_op.upper()
        self.http_mtd = mtd_info[0]
        self.args_count = mtd_info[1]
        self.opts = list(mtd_info[2]) + ['retry']

    def api(self, *args, **argkv):
        mtd_args = []

        for idx in range(self.args_count):
            if idx < len(args):
                mtd_args.append(args[idx])

            else:
                left_cnt = self.args_count - len(mtd_args)
                opt_name = self.opts[-left_cnt]
                mtd_args.append(argkv.get(opt_name, None))

        retry = mtd_args.pop()

        qs = {}
        # retry in opts, but it is not in qs
        qs_keys = list(self.opts[:-1])
        while len(qs_keys) > 0:
            qs[qs_keys.pop()] = mtd_args.pop()

        body = None
        if self.http_mtd == 'PUT':
            body = utfjson.dump(mtd_args.pop())

        path = [self.redis_op] + mtd_args

        return self.cli._api(self.http_mtd, retry, path, body, qs)


class RedisProxyClient(object):

    # redis operation, http method, count of args, optional args name
    methods = {
        # get(key, retry=0)
        'get': ('get', 'GET', 2, ()),

        # set(key, val, expire=None, retry=0)
        'set': ('set', 'PUT', 4, ('expire',)),

        # hget(hashname, hashkey, retry=0)
        'hget': ('hget', 'GET', 3, ()),

        # hset(hashname, hashkey, val, expire=None, retry=0)
        'hset': ('hset', 'PUT', 5, ('expire',)),

        # hkeys(hashname, retry=0)
        'hkeys': ('hkeys', 'GET', 2, ()),

        # hvals(hashname, retry=0)
        'hvals': ('hvals', 'GET', 2, ()),

        # hgetall(hashname, retry=0)
        'hgetall': ('hgetall', 'GET', 2, ()),

        # delete(key, retry=0)
        'delete': ('del', 'DELETE', 2, ()),

        # hdel(hashname, key, retry=0)
        'hdel': ('hdel', 'DELETE', 3, ()),
    }

    def __init__(self, hosts, proxy_hosts=None, nwr=None, ak_sk=None, timeout=None):
        self.hosts = hosts
        self.proxy_hosts = proxy_hosts

        if nwr is None:
            nwr = config.rp_cli_nwr

        if ak_sk is None:
            ak_sk = config.rp_cli_ak_sk

        self.n, self.w, self.r = nwr
        self.access_key, self.secret_key = ak_sk

        self.timeout = timeout or DEFAULT_TIMEOUT
        self.ver = '/redisproxy/v1'

        for mtd_name, mtd_info in self.methods.items():
            api_obj = SetAPI(self, mtd_info[0], mtd_info[1:])
            setattr(self, mtd_name, api_obj.api)

    def _sign_req(self, req):
        sign_payload = True if 'body' in req else False
        signer = awssign.Signer(self.access_key, self.secret_key)
        sign_ctx = signer.add_auth(req, query_auth=True, sign_payload=sign_payload)
        logger.debug('signing details: {ctx}'.format(ctx=sign_ctx))

    def _make_req_uri(self, params, qs):
        path = [self.ver]
        path.extend(params)

        qs_list = [
            'n={n}'.format(n=self.n),
            'w={w}'.format(w=self.w),
            'r={r}'.format(r=self.r),
        ]
        for k, v in qs.items():
            if v is None:
                continue

            qs_list.append('{k}={v}'.format(k=k, v=v))

        return '{p}?{qs}'.format(p='/'.join(path), qs='&'.join(qs_list))

    def _req(self, req):
        if 'headers' not in req:
            req['headers'] = {
                'host': '{ip}:{port}'.format(ip=self.ip, port=self.port),
            }

        elif 'host' not in req['headers']:
            req['headers']['host'] = '{ip}:{port}'.format(ip=self.ip, port=self.port)

        body = req.get('body', None)
        if body is not None:
            req['headers']['Content-Length'] = len(body)

        self._sign_req(req)

        cli = http.Client(self.ip, self.port, self.timeout)
        cli.send_request(req['uri'], method=req['verb'], headers=req['headers'])
        if body is not None:
            cli.send_body(req['body'])

        cli.read_response()
        res = cli.read_body(None)

        msg = 'Status:{s} req:{req} res:{res} server:{ip}:{p}'.format(
              s=cli.status, req=repr(req), res=repr(res),
              ip=self.ip, p=self.port)

        if cli.status == 404:
            raise KeyNotFoundError(msg)

        elif cli.status != 200:
            raise ServerResponseError(msg)

        return res

    @_proxy
    @_retry
    def _api(self, verb, path, body, qs):
        req = {
            'verb': verb,
            'uri': self._make_req_uri(path, qs),
        }

        if body is not None:
            req['body'] = body

        if verb == 'GET':
            rst = self._req(req)
            return utfjson.load(rst)

        else:
            self._req(req)
