<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)

  - [Request](#request)
- [Methods](#methods)
  - [Request.aws_sign](#requestaws_sign)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

request

represents a http request including a normal request and  an aws version 4 signature request 

#   Status

This library is considered production ready.

#   Synopsis

```python
bucket_name = 'your bucket name'
key_name = 'your key'
endpoint = 'the endpoint'

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
    'do_add_auth': 1
}
request1 = Request(dict1)

# content can be a file or str in post request
request1.content = "send post request"
# whether call function aws_sign() according to 'do_add_auth' value
request1.aws_sign(access_key, secret_key, request_date='20180917T120101Z')
# send request
conn = http.Client(host, port)
conn.send_request(request1['uri'], method='POST', headers=request1['headers'])
conn.send_body(request1['body'])
resp = conn.read_response()
```

#   Description
Request represents a http request including a normal request and  an aws version 4 signature request
You need to provide a python dict which represent your request(it typically contains 'verb',
'uri', 'args', 'headers', 'body', 'fields', 'do_add_auth'), and your access key and secret key.
This lib will create a http request and add signature to the request(do_add_auth is True) by call function aws_sign().

#   Classes

## Request

**syntax**
`request1 = request.Request(dict)`

**argument**

-   `dict`
    a python dict which used to represent your request.
    It may contain the following fields:

    -   `verb`:
        the request method, such as 'GET', 'PUT', 'POST'. Required.

    -   `uri`:
        the url encoded uri. In PUT/GET request, it can contain query string
        only when you did not specify `args` in `request`. Required.

    -   `args`:
        a python dict contains the request parameters, it should not be
        url encoded. You can not use both `args` and query string in `uri`
        at the same time. Generally this attribute is null in post request.

    -   `headers`:
        a python dict contains request headers. It must contains the
        'Host' header.

    -   `body`:
        a string contains the request payload. In non-post request, If you do not want to sign
        the payload or you have set 'X-Amz-ContentSHA256' header in `headers`,
        you can omit this field. In POST request, when provide a dict, body
        is null, body is obtained by the fields,

    -   'fields': a python dict which contains form fields. Only the post reqeust the
        fields is not {}, other situations the value is {}.It may contain the following attributes:
        
        -   `Policy`:
            is python dict, describing what is permitted in POST request.
            After calling aws_sign() function, it will be replaced by it's base64
            encoded version.

        -   `key`:
            the key of the object to upload.

        It also support some other fields, more infomation at
        [here](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPOST.html)
        This method will add some signature related fields to this dict.

    -   'do_add_auth':
        a bool number to mark whether the request needs to add auth. When the
        value is True, the request needs to call the aws_sign() to update the request.

##  Request.aws_sign

The method is used to get a signed request. Only when 'do_add_auth' is True,
this function can be called.

**syntax**
`request1.aws_sign(access_key, secret_key, query_auth=query_auth, sign_payload=sign_payload,
    headers_not_to_sign=headers_not_to_sign, request_date=request_date, signing_date=signing_date,
    region=region, service=service, expires=expires)`

**arguments**

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
    needed  to be signed. Generally, only non-post request may need it. Optional.

-   `request_date`:
    timestamp or a iso base format date string, used to specify
    a custom request date, instead of using current time as request date.
    Optional.

-   `signing_date`:
    is a 8 digital date string like '20170131', used to specify a
    custom signing date. Optional.

-   `region`:
    the region name of the service, the default is 'us-east-1'.

-   `serive`:
    the service name, the default is 's3'.

-   `expires`:
    specify the signature expire time in seconds.
    It will overwrite the value of `default_expires`. Optional.

#   Author

Hubiyong (胡碧勇) <biyong.hu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2018 Hubiyong (胡碧勇) <biyong.hu@baishancloud.com>
