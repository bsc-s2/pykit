<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Exceptions](#exceptions)
    - [http.HttpError](#httphttperror)
    - [http.LineTooLongError](#httplinetoolongerror)
    - [http.ChunkedSizeError](#httpchunkedsizeerror)
    - [http.NotConnectedError](#httpnotconnectederror)
    - [http.ResponseNotReadyError](#httpresponsenotreadyerror)
    - [http.HeadersError](#httpheaderserror)
    - [http.BadStatusLineError](#httpbadstatuslineerror)
- [Constants](#constants)
    - [http.Client.status](#httpclientstatus)
    - [http.Client.has_read](#httpclienthas_read)
    - [http.Client.headers](#httpclientheaders)
    - [http.Client.content_length](#httpclientcontent_length)
    - [http.Client.chunked](#httpclientchunked)
- [Classes](#classes)
    - [http.Client](#httpclient)
- [Methods](#methods)
    - [http.Client.send_request](#httpclientsend_request)
    - [http.Client.read_status](#httpclientread_status)
    - [http.Client.read_headers](#httpclientread_headers)
    - [http.Client.read_response](#httpclientread_response)
    - [http.Client.request](#httpclientrequest)
    - [http.Client.send_body](#httpclientsend_body)
    - [http.Client.read_body](#httpclientread_body)
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

    # send http reqeust without body
    # read response status line
    # read response headers
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
    print(h.read_body(None))
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

    # send http reqeust
    h.send_request('http://www.example.com', method='POST', headers=headers)

    # send http request body
    h.send_body(content)

    # read response status line and headers
    status, headers = h.read_response()

    # read response body
    print(h.read_body(None))
except (socket.error, http.HttpError) as e:
    print(repr(e))
```

#   Description

HTTP/1.1 client

We find that `httplib` must work in blocking mode and it can not have a timeout
when recving response.

Use this module, we can set timeout, if timeout raise a `socket.timeout`.

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
Raise if length of line is greater or equal than 65536
when read response status line,  headers and get length of chunked block.

##  http.ChunkedSizeError

**syntax**:
`http.ChunkedSizeError`

A subclass of `HttpError`.
Raise if failed to get length of chunked block.

##  http.NotConnectedError

**syntax**:
`http.NotConnectedError`

A subclass of `HttpError`.
Raise if send data without connecting to server.

##  http.ResponseNotReadyError

**syntax**:
`http.ResponseNotReadyError`

A subclass of `HttpError`.
Raise if response is unavailable.

##  http.HeadersError

**syntax**:
`http.HeadersError`

A subclass of `HttpError`.
Raise if failed to read response headers.

##  http.BadStatusLineError

**syntax**:
`http.BadStatusLineError`

A subclass of `HttpError`.
Raise if failed to read response status line.

#   Constants

##  http.Client.status

**syntax**:
`http.Client.status`

Status code returned by server.

##  http.Client.has_read

**syntax**:
`http.Client.has_read`

The length of response body that has been read.

##  http.Client.headers

**syntax**:
`http.Client.headers`

A `dict`(header name, header value) of response headers.

##  http.Client.content_length

**syntax**:
`http.Client.content_length`

Length of http response body, if body is chunked encoding,
it is `None`.

##  http.Client.chunked

**syntax**:
`http.Client.chunked`

Whether response body is chunked encoding or not.

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

Connect to server and send http request.

**arguments**:

-   `uri`:
    specifies the object being requested

-   `method`:
    specifies an HTTP request method

-   `headers`:
    a `dict`(header name, header value) of http request headers

**return**:
nothing

##  http.Client.read_status

**syntax**:
`http.Client.read_status()`

Read response status line and return the status code.
Cache the response status code with `http.Client.status`

**arguments**:
nothing

**return**:
response status code.

##  http.Client.read_headers

**syntax**:
`http.Client.read_headers()`

Read and return the response headers.
Cache the response headers with `http.Client.headers`

**arguments**:
nothing

**return**:
response headers, it is a `dict`(header name , header value).

##  http.Client.read_response

**syntax**:
`http.Client.read_response()`

Read response status line, headers and return them.
Cache the status code with `http.Client.status`
Cache the response headers with `http.Client.headers`

**arguments**:
nothing

**return**: two values,

-   status: response status code, type is `int`

-   headers: response headers, it is a `dict`(header name , header value).

##  http.Client.request

**syntax**:
`http.Client.request(uri, method='GET', headers={})`

Send http request without body and read response status line, headers.
After it, get response status code with `http.Client.status`,
get response headers with `http.Client.headers`.

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

Send http request body. It should be a `str` of data
to send after the headers are finished

**arguments**:

-   `body`:
    a `str` of http request body.

**return**:
nothing

##  http.Client.read_body

**syntax**:
`http.Client.read_body(size)`

Read and return the response body.

**arguments**:

-   `size`:
    need read size, if greater than left size use the min one,
    if `None` read left unread body.

**return**:
the response body.

#   Author

Baohai Liu(刘保海) <baohai.liu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Baohai Liu(刘保海) <baohai.liu@baishancloud.com>
