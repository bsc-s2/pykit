#!/usr/bin/env python
#coding: utf-8

import os.path
import uuid
import errno
import copy

from pykit import mime
from collections import Iterator


class MultipartError(Exception):
    pass


class InvalidArgumentTypeError(MultipartError):
    pass


class Multipart(object):

    def __init__(self, block_size=1024 * 1024):
        self.block_size = block_size

        self.boundary = uuid.uuid4().hex

        self.delimiter = '--{b}'.format(b=self.boundary)
        self.terminator = '--{b}--'.format(b=self.boundary)

    def make_headers(self, fields, headers=None):
        if headers is None:
            headers = {}
        else:
            headers = copy.deepcopy(headers)

        headers['Content-Type'] = ('multipart/form-data; '
            'boundary={b}'.format(b=self.boundary))

        if 'Content-Length' not in headers:
            headers['Content-Length'] = self._get_body_size(fields)

        return headers

    def make_body_reader(self, fields):
        for f in fields:
            reader, fsize, headers = self._standardize_field(
                f['name'], f['value'], f.get('headers', {}))

            yield self._get_field_header(headers)

            for buf in reader:
                yield buf

            yield '\r\n'

        yield self.terminator

    def _standardize_field(self, name, value, headers):
        if isinstance(value, str):
            reader = self._make_str_reader(value)
            fsize = len(value)
            self._set_content_disposition(headers, name)

            return reader, fsize, headers

        elif isinstance(value, list):
            reader, fsize, fname = self._standardize_value(value)

            self._set_content_disposition(headers, name, fname)
            if fname is not None:
                headers.setdefault('Content-Type', mime.get_by_filename(fname))

            return reader, fsize, headers

        raise InvalidArgumentTypeError(
            'type of value {x} is invalid'.format(x=type(value)))

    def _standardize_value(self, value):
        reader, fsize, fname = (value + [None, None])[:3]

        if isinstance(reader, file):
            reader = self._make_file_reader(reader)

        elif isinstance(reader, str):
            reader = self._make_str_reader(reader)
            fsize = len(value[0])

        elif isinstance(reader, Iterator):
            pass

        else:
            raise InvalidArgumentTypeError('type of value[0] {x}'
                'is invalid'.format(x=type(value[0])))

        return reader, fsize, fname

    def _get_field_size(self, field):
        reader, fsize, headers = self._standardize_field(
            field['name'], field['value'], field.get('headers', {}))

        field_headers = self._get_field_header(headers)

        return len(field_headers) + fsize + len('\r\n')

    def _get_body_size(self, fields):
        body_size = 0

        for f in fields:
            body_size += self._get_field_size(f)

        return body_size + len(self.terminator)

    def _get_field_header(self, headers):
        field_headers = [self.delimiter]

        field_headers.append('Content-Disposition: ' +
            headers.pop('Content-Disposition'))

        for k, v in headers.items():
            field_headers.append(k+': '+v)

        field_headers.extend([''] * 2)

        return '\r\n'.join(field_headers)

    def _make_file_reader(self, file_object):
        while True:
            buf = file_object.read(self.block_size)
            if buf == '':
                break
            yield buf

    def _make_str_reader(self, data):
        yield data

    def _set_content_disposition(self, headers, name, fname=None):
        if fname is None:
            headers['Content-Disposition'] = (
                    'form-data; name={n}'.format(n=name))
        else:
            headers['Content-Disposition'] = (
                'form-data; name={n}; filename={fn}'.format(n=name, fn=fname))
