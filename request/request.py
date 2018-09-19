#!/usr/bin/env python2
# coding: utf-8

import sys
import os
from pykit import awssign
from pykit import httpmultipart
from pykit.dictutil import FixedKeysDict


class InvalidRequestError(Exception):
    pass


class InvalidArgumentError(Exception):
    pass


class InvalidMethodCall(Exception):
    pass


def _str(arg=''):
    return arg


class Request(FixedKeysDict):
    keys_default = dict((('verb', _str),
                         ('uri', _str),
                         ('args', dict),
                         ('headers', dict),
                         ('body', _str),
                         ('fields', dict),
                         ('do_add_auth', bool),))

    def __init__(self, *args, **argkv):

        # content represents str or a file to  upload in POST request
        self.content = None
        super(FixedKeysDict, self).__init__(*args, **argkv)

        if self['verb'] == 'POST' and self['fields'] == {}:
            raise InvalidRequestError('POST request needs fields attribute ')

        if self['verb'] != 'POST' and self['fields'] != {}:
            raise InvalidRequestError('non POST request must not contain fields attribute')

        if self['verb'] == 'POST' and self['body'] != '':
            raise InvalidRequestError('body is made by fields in post request')

        if self['verb'] == 'POST':
            if self['do_add_auth'] == False:
                self['body'], self['headers'] = self._init_body_headers()

    def aws_sign(self, access_key, secret_key, query_auth=False, sign_payload=False, headers_not_to_sign=[],
                 request_date=None, signing_date=None, region='us-east-1', service='s3', expires=60):

        if self['do_add_auth'] == False:
            raise InvalidMethodCall('only add_auth request can call this method')

        signer = awssign.Signer(access_key, secret_key, region=region, service=service, default_expires=expires)

        if self['verb'] == 'POST':
            res = signer.add_post_auth(self['fields'], request_date=request_date, signing_date=signing_date)
            self['body'], self['headers'] = self._make_body_headers()
            return res
        else:
            res = signer.add_auth(self, query_auth=query_auth, sign_payload=sign_payload,
                                  headers_not_to_sign=headers_not_to_sign, request_date=request_date, signing_date=signing_date)
            return res

    def _init_body_headers(self):

        fields = self['fields']
        headers = self['headers']
        multipart_cli = httpmultipart.Multipart()
        multipart_fields = []

        for k, v in fields.iteritems():
            multipart_fields.append({'name': k, 'value': v})

        body_reader =  multipart_cli.make_body_reader(multipart_fields)
        data = []
        for body in body_reader:
            data.append(body)
        res_body = ''.join(data)
        headers = multipart_cli.make_headers(multipart_fields, headers)

        return res_body, headers

    def _make_body_headers(self):

        fields = self['fields']
        headers = self['headers']
        multipart_cli = httpmultipart.Multipart()
        multipart_fields = []
        content = self.content

        for k, v in fields.iteritems():
            multipart_fields.append({'name': k, 'value': v})

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
            raise InvalidArgumentError('content to upload must be a file or str')

        headers = multipart_cli.make_headers(multipart_fields, headers)
        body_reader =  multipart_cli.make_body_reader(multipart_fields)
        data = []
        for body in body_reader:
            data.append(body)
        res_body = ''.join(data)

        return res_body, headers
