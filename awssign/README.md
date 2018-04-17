<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Classes](#classes)
  - [Signer](#signer)
- [Methods](#methods)
  - [Signer.add_auth](#signeradd_auth)
  - [Singer.add_post_auth](#singeradd_post_auth)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

awssign

A python lib is used for adding aws version 4 signature to request.

#   Status

This library is considered production ready.

#   Synopsis

```python
from pykit import awssign
import httplib

access_key = 'your access key'
secret_key = 'your secret key'

signer = awssign.Signer(access_key, secret_key)

file_content = 'bla bla'
request = {
    'verb': 'PUT',
    'uri': '/test-bucket/test-key',
    'args': {
        'foo2': 'bar2',
        'foo1': True,
        'foo3': ['bar3', True],
    },
    'headers': {
        'Host': 'bscstorage.com',
        'Content-Length': len(file_content),
    },
    'body': file_content,
}

signer.add_auth(request, sign_payload=True)

conn = httplib.HTTPConnection('ss.bscstorage.com')
conn.request(request['verb'], request['uri'],
             request['body'], request['headers'])
resp = conn.getresponse()
```

#   Description

This lib is used to sign a request using aws signature version 4. You
need to provide a python dict which represent your request(it typically
contains `verb`, `uri`, `args`, `headers`, `body`), and your access key
and your secret key. This lib will add signature to the request.

#   Classes

## Signer

**syntax**
`signer = awssign.Signer(access_key, secret_key, **kwargs)`

**arguments**

-   `access_key`:
    the access key used to sign the request.

-   `secret_key`:
    the secret key used to sign the request.

-   `kwargs`:
    following keyword arguments are allowed.

    -   `region`:
    the region name of the service, the default is 'us-east-1'.

    - `serive`:
    the service name, the default is 's3'.

    - `default_expires`:
    the default expires time of a presigned url in seconds,
    the default is 60.

#   Methods

## Signer.add_auth

The method used to sign a request.

**syntax**
`signer.add_auth(request, **kwargs)`

**arguments**

-   `request`:
    a python dict which used to represent your request.
    It may contents the following fields:

    -   `verb`:
        the request method, such as 'GET', 'PUT'. Required.

    -   `uri`:
        the url encoded uri, it can contains query string only when you
        did not specify `args` in `request`. Required.

    -   `args`:
        a python dict contains the request parameters, it should not be
        url encoded. You can not use both `args` and query string in `uri`
        at the same time.

    -   `headers`:
        a python dict contains request headers. It must contains the
        'Host' header.

    -   `body`:
        a string contains the request payload. If you do not want to sign
        the payload or you have set 'X-Amz-ContentSHA256' header in `headers`,
        you can omit this field.

-   `kwargs`:
    following keyword arguments are allowed.

    -   `query_auth`:
        set to `True` if you want to add the signature to the query string.
        The default is `False`, mean add the signature in the header.

    -   `sign_payload`:
        set to `True` if you want to sign the payload.
        The default is `False`.

    -   `headers_not_to_sign`:
        a list of header names, used to indicate which headers are
        not need to be signed. Optional.

    -   `request_date`:
        timestamp or a iso base format date string, used to specify
        a custom request date, instead of using current time as request date.
        Optional.

    -   `expires`:
        specify the signature expire time in seconds.
        It will overwrite the value of `default_expires`. Optional.

    -   `signing_date`:
        is a 8 digital date string like '20170131', used to specify a
        custom signing date. Optional.

##  Singer.add_post_auth

The method used to sign a browser based post request.

**syntax**
`signer.add_post_auth(fields, **kwargs)`

**arguments**

-   `fields`:
    a python dict which contains form fields.
    It may contents the following fields:

    -   `Policy`:
        is python dict, describing what is permitted in the request.
        After this function call, it will be replaced by it's base64
        encoded version.

    -   `key`:
        the key of the object to upload.

    It also support some other fields, more infomation at
    [here](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPOST.html)
    This method will add some signature related fields to this dict.

-   `kwargs`:
    following keyword arguments are allowed.

    -   `request_date`:
        the same as in `add_auth`.

    -   `signing_date`:
        the same as in `add_auth`.

#   Author

Renzhi (任稚) <zhi.ren@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2016 Renzhi (任稚) <zhi.ren@baishancloud.com>
