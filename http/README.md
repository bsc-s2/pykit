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
  - [http.Client.get_trace_str](#httpclientget_trace_str)
  - [http.headers_add_host](#httpheaders_add_host)
  - [http.request_add_host](#httprequest_add_host)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

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
`http.Client(host, port, timeout=60, stopwatch_kwargs=None, https_context=None)`

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

-   `stopwatch_kwargs`:
    is an dictionary used as keyword arguments when initializing stopwatch instance.

    ```
    class StopWatch(object):
        def __init__(self,
                     strict_assert=True,
                     export_tracing_func=None,
                     export_aggregated_timers_func=None,
                     max_tracing_spans_for_path=1000,
                     min_tracing_milliseconds=3,
                     time_func=None):
    ```

-   `https_context`:
    a `ssl.SSLContext` instance describing the various SSL options. Defaults to `None`.

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

##  http.Client.readlines

**syntax**:
`http.Client.readlines(delimiter)`

Read and yield one line in response body each time.

**arguments**:

-   `delimiter`:
    specify the delimiter between each line, defalut supporting `\n`.

**return**:
a generator yileding one line including delimiter in response body each time.

##  http.Client.get_trace_str

**syntax**:
`http.Client.get_trace_str()`

**return**:
a string shows time spent on each phase of a request.
The following fields would presents in it:

```
conn: 0.000001 -; send_header: 0.000000 -; recv_status: 0.000000 -; recv_header: 0.000000 -; recv_body: 0.000000 -; recv_body: 0.000000 -; exception: 0.000000 -; pykit.http.Client: 0.000002 Exception:ValueError
```

The numbers are time in second.

There might be less fields in the result, if request failed.

It is also possible some of the above fields appear more than once.

For example if a server responds a `100-Continue` status line and a `200-OK`
status line, there would be two `recv_status` fields.

If the caller calls `http.Client.read_body` more than one time, there would be
more than one `recv_body` fields.

##  http.headers_add_host

**syntax**:
`http.headers_add_host(headers, address)`

If there is no Host field in the headers, insert the address as a Host into the headers.

**arguments**:

-   `headers`:
    a `dict`(header name, header value) of http request headers

-   `address`:
    a `string` represents a domain name

**return**:
    headers after adding

##  http.request_add_host

**syntax**:
`http.request_add_host(request, address)`

If the request has no headers field, or request['headers'] does not have a Host field, then add address to Host.

**arguments**:

-   `request`:
    a `dict`(request key, request name) of http request

-   `address`:
    a `string` represents a domain name

**return**:
    request after adding

#   Author

Baohai Liu(刘保海) <baohai.liu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Baohai Liu(刘保海) <baohai.liu@baishancloud.com>
