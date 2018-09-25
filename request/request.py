#!/usr/bin/env python2
# coding: utf-8

import os
from pykit import awssign
from pykit import httpmultipart
from pykit.dictutil import FixedKeysDict


class RequestError(Exception):
    pass


class InvalidRequestError(RequestError):
    pass


class InvalidArgumentError(RequestError):
    pass


class InvalidMethodCall(RequestError):
    pass


# the arg  must be str or unicode type
def _basestring(arg=''):
    if not isinstance(arg, basestring):
        raise InvalidArgumentError(
            'type of arg should be str or unicode, get {t}'.format(t=type(arg)))

    return arg


def _get_sign_args(auth_args=None):

    if auth_args is None:
        return {}

    if not isinstance(auth_args, dict):
        raise InvalidArgumentError(
            'type of auth_args should be dict, got {t}'.format(t=type(auth_args)))

    if 'access_key' not in auth_args:
        raise InvalidArgumentError('add_auth request must contain access key')

    if 'secret_key' not in auth_args:
        raise InvalidArgumentError('add_auth request must contain secret key')

    rst = {
        'query_auth': False,
        'sign_payload': False,
        'headers_not_to_sign': [],
        'request_date': None,
        'signing_date': None,
        'region': 'us-east-1',
        'service': 's3',
        'expires': 60,
    }

    rst.update(auth_args)

    return rst


def _make_post_body_headers(fields, headers, content, do_add_auth=False):

    multipart_cli = httpmultipart.Multipart()
    multipart_fields = []

    for k, v in fields.iteritems():
        multipart_fields.append({'name': k, 'value': v})

    if do_add_auth:
        if content is None:
            multipart_fields.append({
                'name': 'file',
                'value': '',
                })

        elif isinstance(content, str):
            multipart_fields.append({
                'name': 'file',
                'value': content,
                })

        elif isinstance(content, file):
            multipart_fields.append({
                'name': 'file',
                'value': [content, os.fstat(content.fileno()).st_size,
                          os.path.basename(content.name)],
                })

        else:
            raise InvalidArgumentError(
                'type of content should be str or unicode, get {t}'.format(t=type(content)))

    body_reader = multipart_cli.make_body_reader(multipart_fields)
    data = []

    for body in body_reader:
        data.append(body)

    res_body = ''.join(data)
    headers = multipart_cli.make_headers(multipart_fields, headers)

    return res_body, headers


class Request(FixedKeysDict):

    keys_default = dict((('verb', _basestring),
                         ('uri', _basestring),
                         ('args', dict),
                         ('headers', dict),
                         ('body', _basestring),
                         ('fields', dict),
                         ('sign_args', _get_sign_args),))

    def __init__(self, *args, **argkv):
        # content represents str or a file to upload in post request
        self.content = None

        if 'content' in argkv:
            self.content = argkv['content']
            del argkv['content']

        super(Request, self).__init__(*args, **argkv)

        region = self['sign_args']['region']
        service = self['sign_args']['service']
        expires = self['sign_args']['expires']
        access_key = self['sign_args']['access_key']
        secret_key = self['sign_args']['secret_key']

        query_auth = self['sign_args']['query_auth']
        sign_payload = self['sign_args']['sign_payload']
        request_date = self['sign_args']['request_date']
        signing_date = self['sign_args']['signing_date']
        headers_not_to_sign = self['sign_args']['headers_not_to_sign']

        signer = awssign.Signer(access_key, secret_key, region=region,
                                service=service, default_expires=expires)

        if self['verb'] != 'POST' and self.content is not None:
            raise InvalidRequestError(
                'content should be empty in non post request')

        if self['verb'] == 'POST':
            if len(self['fields']) == 0:
                raise InvalidRequestError('fields can not be empty in post request')

            if self['body'] != '':
                raise InvalidRequestError(
                    'body in init dict should be empty in post request')

            if len(self['sign_args']) != 0:
                signer.add_post_auth(self['fields'], request_date=request_date,
                                     signing_date=signing_date)

                self['body'], self['headers'] = _make_post_body_headers(
                    self['fields'], self['headers'], self.content, do_add_auth=True)

            else:
                self['body'], self['headers'] = _make_post_body_headers(
                    self['fields'], self['headers'], self.content, do_add_auth=False)

        else:
            if self['fields']:
                raise InvalidRequestError('fields should be empty in non post request')

            if self['sign_args']:
                signer.add_auth(self, query_auth=query_auth,
                                sign_payload=sign_payload,
                                request_date=request_date,
                                signing_date=signing_date,
                                headers_not_to_sign=headers_not_to_sign)
