#!/usr/bin/env python2
# coding: utf-8

import copy

def headers_add_host(headers, address):

    headers.setdefault('Host', address)

    return headers

def request_add_host(request, address):

    request.setdefault('headers', {})
    request['headers'].setdefault('Host', address)

    return request
