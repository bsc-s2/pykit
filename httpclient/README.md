<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Constants](#constants)
    - [httpclient.HttpClient.status](#httpclienthttpclientstatus)
    - [httpclient.HttpClient.has_read](#httpclienthttpclienthasread)
    - [httpclient.HttpClient.headers](#httpclienthttpclientheaders)
    - [httpclient.HttpClient.content_length](#httpclienthttpclientcontentlength)
    - [httpclient.HttpClient.chunked](#httpclienthttpclientchunked)
- [Exceptions](#exceptions)
    - [httpclient.HttpError](#httpclienthttperror)
    - [httpclient.LineTooLongError](#httpclientlinetoolongerror)
    - [httpclient.ChunkedSizeError](#httpclientchunkedsizeerror)
    - [httpclient.NotConnectedError](#httpclientnotconnectederror)
    - [httpclient.ResponseNotReadyError](#httpclientresponsenotreadyerror)
    - [httpclient.HeadersError](#httpclientheaderserror)
    - [httpclient.BadStatusLineError](#httpclientbadstatuslineerror)
- [Classes](#classes)
    - [httpclient.HttpClient](#httpclienthttpclient)
- [Methods](#methods)
    - [httpclient.HttpClient.send_request](#httpclienthttpclientsendrequest)
    - [httpclient.HttpClient.read_headers](#httpclienthttpclientreadheaders)
    - [httpclient.HttpClient.request](#httpclienthttpclientrequest)
    - [httpclient.HttpClient.send_body](#httpclienthttpclientsendbody)
    - [httpclient.HttpClient.read_body](#httpclienthttpclientreadbody)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

#   Name

httpclient

#   Status

The library is considered production ready.

#   Synopsis

```python
from pykit import httpclient

headers = {
    'Host': '127.0.0.1',
    'Accept-Language': 'en, mi',
}

try:
    h = httpclient.HttpClient('127.0.0.1', 80)
    # send http reqeust and recv http response headers
    h.request('/test.txt', method='GET', headers=headers)
    status = h.status
    # response code return from http server, type is int
    # 200
    # 302
    # 404
    # ...

    res_headers = h.headers
    # response headers except status line
    # res_headers = {
    #   'Content-Type': 'text/html;charset=utf-8',
    #   'Content-Length': 1024,
    #   ...
    # }

    # get response body
    body = ''
    while True:
        buf = h.read_body(1024)
        if len(buf) <= 0:
            break
        body += buf

    print(body)
except (socket.error, httpclient.HttpError) as e:
    print(repr(e))
```

```python
from pykit import httpclient
import urllib

content = urllib.urlencode({'f': 'foo', 'b': 'bar'})
headers = {
    'Host': 'www.example.com',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    'Content-Length': len(content),
}

try:
    h = httpclient.HttpClient('127.0.0.1', 80)
    # send http reqeust header
    h.send_request('http://www.example.com', method='POST', headers=headers)
    # send http request body
    h.send_body(content)
    # get response headers
    res_headers = h.read_headers()
    status = h.status
    # get response body
    body = ''
    while True:
        buf = h.read_body(1024)
        if len(buf) <= 0:
            break
        body += buf

    print(body)

except (socket.error, httpclient.HttpError) as e:
    print(repr(e))
```

#   Description

HTTP/1.1 client

#   Constants

##  httpclient.HttpClient.status

**syntax**:
`httpclient.HttpClient.status`

Status code returned by server.

##  httpclient.HttpClient.has_read

**syntax**:
`httpclient.HttpClient.has_read`

Has read length of response body

##  httpclient.HttpClient.headers

**syntax**:
`httpclient.HttpClient.headers`

A `dict`(header name, header value) of response headers.

##  httpclient.HttpClient.content_length

**syntax**:
`httpclient.HttpClient.content_length`

Http resonse body length, if body is chunked encoding,
it is `None`.

##  httpclient.HttpClient.chunked

**syntax**:
`httpclient.HttpClient.chunked`

Http response body encoding type, `True` is chunked encoding,
`False` is other encoding.

#   Exceptions

##  httpclient.HttpError

**syntax**:
`httpclient.HttpError`

The base class of the other exceptions in this module.
It is a subclass of `Exception`.

##  httpclient.LineTooLongError

**syntax**:
`httpclient.LineTooLongError`

A subclass of `HttpError`.
Raise if length of line is greater than 65536
when read response headers or get length of chunked block.

##  httpclient.ChunkedSizeError

**syntax**:
`httpclient.ChunkedSizeError`

A subclass of `HttpError`.
Raise if get length of chunked block failed.

##  httpclient.NotConnectedError

**syntax**:
`httpclient.NotConnectedError`

A subclass of `HttpError`.
Raise if send data without connecting to server.

##  httpclient.ResponseNotReadyError

**syntax**:
`httpclient.ResponseNotReadyError`

A subclass of `HttpError`.
Raise if get response without `send_request`.

##  httpclient.HeadersError

**syntax**:
`httpclient.HeadersError`

A subclass of `HttpError`.
Raise when get response headers failed.

##  httpclient.BadStatusLineError

**syntax**:
`httpclient.BadStatusLineError`

A subclass of `HttpError`.
Raise if get response status failed.

#   Classes

##  httpclient.HttpClient

**syntax**:
`httpclient.HttpClient(host, port, timeout=60)`

HTTP client class

**arguments**:

-   `host`:
    server address, ip or domain, type is `str`

-   `port`:
    server port, type is `int`

-   `timeout`:
    set a timeout on blocking socket operations, unit is second, default is 60.
    The value argument can be a nonnegative float expressing seconds, or `None`.
    if `None`, it is equivalent to `socket.setblocking(1)`.
    if `0.0`, it is equivalent to `socket.setblocking(0)`.


#   Methods

##  httpclient.HttpClient.send_request

**syntax**:
`httpclient.HttpClient.send_request(uri, method='GET', headers={})`

Connect to server and send request headers to server.

**arguments**:

-   `uri`:
    specifies the object being requested

-   `method`:
    specifies an HTTP request method

-   `headers`:
    a `dict`(header name, header value) of http request headers

**return**:
nothing

##  httpclient.HttpClient.read_headers

**syntax**:
`httpclient.HttpClient.read_headers()`

Reads and returns the response headers.
The response headers and status code will be cached with
`httpclient.HttpClient.headers` and `httpclient.HttpClient.status`.

**arguments**:
nothing

**return**:
response headers, it is a `dict`(header name , header value).

##  httpclient.HttpClient.request

**syntax**:
`httpclient.HttpClient.request(uri, method='GET', headers={})`

Send http request which doesn't have body and recv response headers.
After it, get response body with `httpclient.HttpClient.read_body`,
get response headers with `httpclient.HttpClient.headers`,
get response status code with `httpclient.HttpClient.status`.

**arguments**:

-   `uri`:
    specifies the object being requested

-   `method`:
    specifies an HTTP request method

-   `headers`:
    a `dict`(header name, header value) of http request headers

**return**:
nothing

##  httpclient.HttpClient.send_body

**syntax**:
`httpclient.HttpClient.send_body(body)`

Send http request body.It should be a `str` of data
to send after the headers are finished

**arguments**:

-   `body`:
    a `str` of http request body.

**return**:
nothing

##  httpclient.HttpClient.read_body

**syntax**:
`httpclient.HttpClient.read_body(size)`

Reads and returns the response body

**arguments**:

-   `size`:
    need read size, if greater than left size, use the min one.

**return**:
the read response body.

#   Author

Baohai Liu(刘保海) <baohai.liu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Baohai Liu(刘保海) <baohai.liu@baishancloud.com>
