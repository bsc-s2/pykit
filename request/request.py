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
            'type of arg is: {x}, should be str or unicode'.format(x=type(arg)))

    return arg


class Request(FixedKeysDict):

    keys_default = dict((('verb', _basestring),
                         ('uri', _basestring),
                         ('args', dict),
                         ('headers', dict),
                         ('body', _basestring),
                         ('fields', dict),
                         ('do_add_auth', bool),))

    def __init__(self, *args, **argkv):
        # content represents str or a file to upload in post request
        self.content = None
        super(FixedKeysDict, self).__init__(*args, **argkv)

        if self['verb'] == 'POST':
            if len(self['fields']) == 0:
                raise InvalidRequestError('fields can not be empty in post request')
            if self['body'] != '':
                raise InvalidRequestError('body in init dict should be empty in post request')
            if not self['do_add_auth']:
                self['body'], self['headers'] = self._make_post_body_headers()

        else:
            if self['fields']:
                raise InvalidRequestError('fields should be empty in non post request')

    def aws_sign(self, access_key, secret_key, query_auth=False, sign_payload=False, headers_not_to_sign=None,
                 request_date=None, signing_date=None, region='us-east-1', service='s3', expires=60):

        if headers_not_to_sign is None:
            headers_not_to_sign = []

        if not self['do_add_auth']:
            raise InvalidMethodCall('non add_auth request can not call aws_sign() method')

        signer = awssign.Signer(access_key, secret_key, region=region, service=service, default_expires=expires)

        if self['verb'] == 'POST':
            ctx = signer.add_post_auth(self['fields'], request_date=request_date, signing_date=signing_date)
            self['body'], self['headers'] = self._make_post_body_headers()

        else:
            ctx = signer.add_auth(self, query_auth=query_auth, headers_not_to_sign=headers_not_to_sign,
                                  sign_payload=sign_payload, request_date=request_date, signing_date=signing_date)

        return ctx

    def _make_post_body_headers(self):

        fields = self['fields']
        headers = self['headers']
        multipart_cli = httpmultipart.Multipart()
        multipart_fields = []
        content = self.content

        for k, v in fields.iteritems():
            multipart_fields.append({'name': k, 'value': v})

        if self['do_add_auth']:
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
                    'value': [content, os.fstat(content.fileno()).st_size, os.path.basename(content.name)],
                    })

            else:
                raise InvalidArgumentError(
                    'type of content is: {x}, should be str or file'.format(x=type(content)))

        body_reader = multipart_cli.make_body_reader(multipart_fields)
        data = []
        for body in body_reader:
            data.append(body)
        res_body = ''.join(data)
        headers = multipart_cli.make_headers(multipart_fields, headers)

        return res_body, headers
