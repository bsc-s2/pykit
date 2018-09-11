<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Exception](#exception)
  - [httpmultipart.MultipartError](#httpmultipartmultiparterror)
  - [httpmultipart.InvalidArgumentTypeError](#httpmultipartinvalidargumenttypeerror)
- [Constants](#constants)
  - [httpmultipart.Multipart.boundary](#httpmultipartmultipartboundary)
  - [httpmultipart.Multipart.block_size](#httpmultipartmultipartblock_size)
- [Classes](#classes)
  - [httpmultipart.Multipart](httpmultipartmultipart)
- [Methods](#methods)
  - [httpmultipart.Multipart.make_headers](#httpmultipartmultipartmake_headers)
  - [httpmultipart.Multipart.make_body_reader](#httpmultipartmultipartmake_body_reader)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

httpmultipart

#   Status

The library is considered production ready.

#   Synopsis

```python
#!usr/bin/env python
#coding: utf-8

import os

from pykit import httpmultipart
from pykit import fsutil

# http request headers
headers = {'Content-Length': 1200}

# http request fields
file_path = '/tmp/abc.txt'
fsutil.write_file(file_path, '123456789')
fields = [
    {
        'name': 'aaa',
        'value': 'abcde',
    },
    {
        'name': 'bbb',
        'value': [open(file_path), os.path.getsize(file_path), 'abc.txt']
    },
]

# get http request headers
multipart = httpmultipart.Multipart()
res_headers = multipart.make_headers(fields, headers=headers)

print res_headers

#output:
#{
#    'Content-Type': 'multipart/form-data; boundary=FormBoundaryrGKCBY7',
#    'Conetnt-Length': 1200,
#}

# get http request body reader
multipart = httpmultipart.Multipart()
body_reader = multipart.make_body_reader(fields)
data = []

for body in body_reader:
    data.append(body)

print ''.join(data)

#output:
#--FormBoundaryrGKCBY7
#Content-Disposition: form-data; name=aaa
#
#abcde
#--FormBoundaryrGKCBY7
#Content-Disposition: form-data; name=bbb; filename=abc.txt
#Content-Type: text/plain
#
#123456789
#--FormBoundaryrGKCBY7--

```

#   Description

This module provides some util methods to get multipart headers and body.

#   Exception

##  httpmultipart.MultipartError

**syntax**:
`httpmultipart.MultipartError`

The base class of the other exceptions in this module.
It is a subclass of `Exception`

##  httpmultipart.InvalidArgumentTypeError

**syntax**:
`httpmultipart.InvalidArgumentTypeError`

A subclass of `MultipartError`
Raise if the type of value is not a str or a list or the type of value[0]
is not a string, string reader, file reader or file object

#   Constants

##  httpmultipart.Multipart.boundary

**syntax**:
`httpmultipart.Multipart.boundary`

a placeholder that represents out specified delimiter

##  httpmultipart.Multipart.block_size

**syntax**:
`httpmultipart.Multipart.block_size`

It represents the size of each reading file

#   Classes

##  httpmultipart.Multipart

**syntax**:
`httpmultipart.Multipart()`

#   Methods

##  httpmultipart.Multipart.make_headers

**syntax**:
`httpmultipart.Multipart.make_headers(fields, headers=None)`

Return a header according to the fields and headers

**arguments**:

-   `fields`:
    is a list of the dict, and each elements contains `name`, `value` and `headers`,
    `headers` is an optional argument

    -   `name`:
    It's a string that represents field's name

    -   `value`:
    The value represents field's content. The type of value can be a string or a
    list, string indicates that the field is a normal string, However, there are
    three arguments of list: `content`, `size` and `file_name`

        -   `content`:
        The type of `content` can be string, reader, file object
            The string type refers to the user want to upload a string. It takes the
        string as the field body

            The reader type refers to a generator. To read the contents of generator as
        the field body

            The file object type refers to a file object, To read the contents of file
        as the field body

        -   `size`
        `size` refers to the length of the content, When the type of `content` is a
        string, size can be None

        - `file_name`
        `file_name` is an optional argument, if `file_name` is None, that indicates
        that `content` is uploaded as a normal field, whereas, the field as a file

    -   `headers`:
    a dict, key is the `field_header_name`, value is the `field_header_value`,
    it contains user defined headers and the required headers, such as
    'Content-Disposition' and 'Content-Type'

-   `headers`:
    a dict of http request headers, key is the `header_name`, value is the
    `header_value`.  It's a default argument and its default value is None

**return**:
a dict that represents the request headers

##  httpmultipart.Multipart.make_body_reader

**syntax**
`httpmultipart.Multipart.make_body_reader(fields)`

Return a body according to the fields

**arguments**:

-  `fields`:
    refer to the explanation above fields

**return**:
a generator that represents the multipart request body

#   Author

Ting Lv(吕婷) <ting.lv@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Ting Lv(吕婷) <ting.lv@baishancloud.com>
