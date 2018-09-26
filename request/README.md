<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Classes](#classes)
  - [Request](#request)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

request

Represents a http request including a normal request and an aws version 4 signature request 

#   Status

This library is considered production ready.

#   Synopsis

```python
#!/usr/bin/env python2
# coding: utf-8

from pykit import http
from pykit import fsutil
from pykit.request import Request

bucket_name = 'your bucket name'
key_name = 'key name to upload'
endpoint = 'endpoint domain name'

# https://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPOST.html
# Host: destinationBucket.endpoint
host = bucket_name + '.' + endpoint
port = portnumber

access_key = 'your access key'
secret_key = 'your secret key'
# create a suitable dict according to verb
dict1 = {
    'verb': 'POST',
    'uri': '/',
    'args': {},
    'headers': {
        'Host': host,
    },
    'body': '',
    'fields': {
        'key': key_name,
        'Policy': {
            'expiration': '2018-09-30T12:00:00.000Z',
            'conditions': [
                ['starts-with', '$key', ''],
                {
                    'bucket': bucket_name,
                },
            ],
        },
    },
    # arguments for add authorization
    'sign_args': {
        'access_key': access_key,
        'secret_key': secret_key,
        'request_date': '20180917T120101Z',
    }
}

# data can be a file or str to upload
request1 = Request(dict1, data = "file or str")

# send request
conn = http.Client(host, port)
conn.send_request(request1['uri'], method=request1['verb'], headers=request1['headers'])
conn.send_body(request1['body'])
resp = conn.read_response()
```

#   Description
Request represents a http request including a normal request and an aws version 4
signature request. You need to provide a python dict which represent your request
(it typically contains `verb`,`uri`, `args`, `headers`, `body`, `fields`, `sign_args`),
and your access key and secret key. Use request class to obtain a http request whicn
can be sent directly.

#   Classes

## Request

**syntax**
`request1 = request.Request(dict)`

**argument**

-   `dict`
    a python dict which used to represent your request.
    It may contain the following fields:

    -   `verb`:
        the request method, such as `GET`, `PUT`, `POST`. Required.

    -   `uri`:
        the url encoded uri. In PUT/GET request, it can contain query string
        only when you did not specify `args` in `request`. Required.

    -   `args`:
        a python dict contains the request parameters, it should not be
        url encoded. You can not use both `args` and query string in `uri`
        at the same time. Generally this attribute is empty in post request.

    -   `headers`:
        a python dict contains request headers. It must contain the `Host` header.

    -   `body`:
        a string contains the request payload. In non-post request, If you do
        not want to sign the payload or you have set `X-Amz-ContentSHA256` header
        in `headers`, you can omit this field. In post request, when provide a dict,
        body is empty, body is obtained by the fields,

    -   `fields`: a python dict which contains form fields. Only the post
        request fields is not empty, other situations fields is empty.
        It may contain the following attributes:
        
        -   `Policy`:
            is python dict, describing what is permitted in post request.
            After the request being signed, it will be replaced by it's
            base64 encoded version.

        -   `key`:
            the key of the object to upload.

        It also support some other fields, more infomation at
        [here](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPOST.html)
        This method will add some signature related fields to this dict.

    -   `sign_args`: a python dict which contain the args to add authorization. It may
        contain the following attributes:

        -   `access_key`:
            the access key used to sign the request.

        -   `secret_key`:
            the secret key used to sign the request.

        -   `query_auth`:
            set to `True` if you want to add the signature to the query string.
            The default is `False`, mean add the signature in the header.
            Generally, only non-post request may need it. Optional

        -   `sign_payload`:
            set to `True` if you want to sign the payload.The default is `False`.
            Generally, only non-post request may need it. Optional

        -   `headers_not_to_sign`:
            a list of header names, used to indicate which headers are not
            needed to be signed. Generally, only non-post request may need it. Optional.

        -   `request_date`:
            timestamp or a iso base format date string, used to specify
            a custom request date, instead of using current time as request date.
            Optional.

        -   `signing_date`:
            is a 8 digital date string like `20170131`, used to specify a
            custom signing date. Optional.

        -   `region`:
            the region name of the service, the default is `us-east-1`.

        -   `serive`:
            the service name, the default is `s3`.

        -   `expires`:
            specify the signature expire time in seconds.
            It will overwrite the value of `default_expires`. Optional.

#   Author

Hubiyong (胡碧勇) <biyong.hu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2018 Hubiyong (胡碧勇) <biyong.hu@baishancloud.com>
