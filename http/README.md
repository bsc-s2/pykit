<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Constants](#constants)
    - [http.Client.status](#httpclientstatus)
    - [http.Client.has_read](#httpclienthasread)
    - [http.Client.headers](#httpclientheaders)
    - [http.Client.content_length](#httpclientcontentlength)
    - [http.Client.chunked](#httpclientchunked)
- [Exceptions](#exceptions)
    - [http.HttpError](#httphttperror)
    - [http.LineTooLongError](#httplinetoolongerror)
    - [http.ChunkedSizeError](#httpchunkedsizeerror)
    - [http.NotConnectedError](#httpnotconnectederror)
    - [http.ResponseNotReadyError](#httpresponsenotreadyerror)
    - [http.HeadersError](#httpheaderserror)
    - [http.BadStatusLineError](#httpbadstatuslineerror)
- [Classes](#classes)
    - [http.Client](#httpclient)
- [Methods](#methods)
    - [http.Client.send_request](#httpclientsendrequest)
    - [http.Client.read_headers](#httpclientreadheaders)
    - [http.Client.request](#httpclientrequest)
    - [http.Client.send_body](#httpclientsendbody)
    - [http.Client.read_body](#httpclientreadbody)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

#   Name

http

#   Status

The library is considered production ready.

#   Synopsis

```python
from pykit import http

headers = {
    'Host': '127.0.0.1',
    'Accept-Language': 'en, mi',
}

try:
    h = http.Client('127.0.0.1', 80)
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
except (socket.error, http.HttpError) as e:
    print(repr(e))
```

```python
from pykit import http
import urllib

content = urllib.urlencode({'f': 'foo', 'b': 'bar'})
headers = {
    'Host': 'www.example.com',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    'Content-Length': len(content),
}

try:
    h = http.Client('127.0.0.1', 80)
    # send http reqeust header
    h.send_request('http://www.example.com', method='POST', headers=headers)
    # send http request body
    h.send_body(content)
    # get response headers
    res_headers = h.read_headers()
    status = h.status
    # get response body
    print(h.read_body(4096))

except (socket.error, http.HttpError) as e:
    print(repr(e))
```

#   Description

HTTP/1.1 client

We find that `httplib` must work in blocking mode and it can not have a timeout
when recving response.

Use this module, we can set timeout, if timeout raise a `socket.timeout`.

#   Constants

##  http.Client.status

**syntax**:
`http.Client.status`

Status code returned by server.

##  http.Client.has_read

**syntax**:
`http.Client.has_read`

Has read length of response body

##  http.Client.headers

**syntax**:
`http.Client.headers`

A `dict`(header name, header value) of response headers.

##  http.Client.content_length

**syntax**:
`http.Client.content_length`

Http resonse body length, if body is chunked encoding,
it is `None`.

##  http.Client.chunked

**syntax**:
`http.Client.chunked`

Http response body encoding type, `True` is chunked encoding,
`False` is other encoding.

#   Exceptions

##  http.HttpError

**syntax**:
`http.HttpError`

The base class of the other exceptions in this module.
It is a subclass of `Exception`.

##  http.LineTooLongError

**syntax**:
`http.LineTooLongError`

A subclass of `HttpError`.
Raise if length of line is greater than 65536
when read response headers or get length of chunked block.

##  http.ChunkedSizeError

**syntax**:
`http.ChunkedSizeError`

A subclass of `HttpError`.
Raise if get length of chunked block failed.

##  http.NotConnectedError

**syntax**:
`http.NotConnectedError`

A subclass of `HttpError`.
Raise if send data without connecting to server.

##  http.ResponseNotReadyError

**syntax**:
`http.ResponseNotReadyError`

A subclass of `HttpError`.
Raise if get response without `send_request`.

##  http.HeadersError

**syntax**:
`http.HeadersError`

A subclass of `HttpError`.
Raise when get response headers failed.

##  http.BadStatusLineError

**syntax**:
`http.BadStatusLineError`

A subclass of `HttpError`.
Raise if get response status failed.

#   Classes

##  http.Client

**syntax**:
`http.Client(host, port, timeout=60)`

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

##  http.Client.send_request

**syntax**:
`http.Client.send_request(uri, method='GET', headers={})`

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

##  http.Client.read_headers

**syntax**:
`http.Client.read_headers()`

Reads and returns the response headers.
The response headers and status code will be cached with
`http.Client.headers` and `http.Client.status`.

**arguments**:
nothing

**return**:
response headers, it is a `dict`(header name , header value).

##  http.Client.request

**syntax**:
`http.Client.request(uri, method='GET', headers={})`

Send http request which doesn't have body and recv response headers.
After it, get response body with `http.Client.read_body`,
get response headers with `http.Client.headers`,
get response status code with `http.Client.status`.

**arguments**:

-   `uri`:
    specifies the object being requested

-   `method`:
    specifies an HTTP request method

-   `headers`:
    a `dict`(header name, header value) of http request headers

**return**:
nothing

##  http.Client.send_body

**syntax**:
`http.Client.send_body(body)`

Send http request body.It should be a `str` of data
to send after the headers are finished

**arguments**:

-   `body`:
    a `str` of http request body.

**return**:
nothing

##  http.Client.read_body

**syntax**:
`http.Client.read_body(size)`

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
