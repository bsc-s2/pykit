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


# the arg must be str or unicode type
def _basestring(arg=''):

    if not isinstance(arg, basestring):
        raise InvalidArgumentError(
            'type of arg should be str or unicode, but {t}'.format(t=type(arg)))

    return arg


def _get_sign_args(sign_args=None):

    if sign_args is None:
        return {}

    if not isinstance(sign_args, dict):
        raise InvalidArgumentError(
            'type of sign_args should be dict, but {t}'.format(t=type(sign_args)))

    if len(sign_args) == 0:
        return {}

    if 'access_key' not in sign_args:
        raise InvalidArgumentError('add authorization request must contain access key')

    if 'secret_key' not in sign_args:
        raise InvalidArgumentError('add authorization request must contain secret key')

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

    rst.update(sign_args)

    return rst


def _make_post_body_headers(fields, headers, body):

    multipart_cli = httpmultipart.Multipart()
    multipart_fields = []

    for k, v in fields.iteritems():
        multipart_fields.append({'name': k, 'value': v})

    if body is None:
        multipart_fields.append({
            'name': 'file',
            'value': '',
        })

    elif isinstance(body, str):
        multipart_fields.append({
            'name': 'file',
            'value': body,
        })

    elif isinstance(body, file):
        multipart_fields.append({
            'name': 'file',
            'value': [body, os.fstat(body.fileno()).st_size, os.path.basename(body.name)],
        })

    else:
        raise InvalidArgumentError(
            'type of body should be str or file, but {t}'.format(t=type(body)))

    body_reader = multipart_cli.make_body_reader(multipart_fields)

    headers = multipart_cli.make_headers(multipart_fields, headers)

    return body_reader, headers


def _make_body_content_length(body):

    if isinstance(body, str):
        content_length = len(body)
        body = _make_str_reader(body)

    elif isinstance(body, file):
        content_length = os.fstat(body.fileno()).st_size
        body = _make_file_reader(body)

    else:
        raise InvalidArgumentError(
            'type of body should be str or file, but {t}'.format(t=type(body)))

    return body, content_length


def _make_str_reader(body):
    yield body


def _make_file_reader(file_obj):
    block_size = 1024 * 1024

    while True:
        buf = file_obj.read(block_size)
        if buf == '':
            break
        yield buf


def _get_body(body=None):
    if body is None:
        return ''

    return body


class Request(FixedKeysDict):

    keys_default = dict((('verb', _basestring),
                         ('uri', _basestring),
                         ('args', dict),
                         ('headers', dict),
                         ('body', _get_body),
                         ('fields', dict),
                         ('sign_args', _get_sign_args),))

    # body represents str or a file to upload
    def __init__(self, to_make_request, body=None):

        super(Request, self).__init__(to_make_request)

        if self['body'] != '':
            raise InvalidRequestError('body should be empty in provided dict')

        if self['verb'] == 'POST':
            if len(self['fields']) == 0:
                raise InvalidRequestError('fields can not be empty in post request')

        else:
            if len(self['fields']) > 0:
                raise InvalidRequestError('fields should be empty in non post request')

            if body is not None:
                self['body'], self['headers']['Content-Length'] = _make_body_content_length(body)

            else:
                self['headers']['Content-Length'] = 0

        do_add_auth = (len(self['sign_args']) != 0)

        if do_add_auth:
            signer = awssign.Signer(self['sign_args']['access_key'],
                                    self['sign_args']['secret_key'],
                                    region=self['sign_args']['region'],
                                    service=self['sign_args']['service'],
                                    default_expires=self['sign_args']['expires'])

        if self['verb'] == 'POST':
            if do_add_auth:
                signer.add_post_auth(self['fields'],
                                     request_date=self['sign_args']['request_date'],
                                     signing_date=self['sign_args']['signing_date'])

            self['body'], self['headers'] = _make_post_body_headers(
                self['fields'], self['headers'], body)

        else:
            if do_add_auth:
                signer.add_auth(self, query_auth=self['sign_args']['query_auth'],
                                sign_payload=self['sign_args']['sign_payload'],
                                request_date=self['sign_args']['request_date'],
                                signing_date=self['sign_args']['signing_date'],
                                headers_not_to_sign=self['sign_args']['headers_not_to_sign'])
