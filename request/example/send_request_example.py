#!/usr/bin/env python2
# coding: utf-8

import httplib
import sys
from pykit import http
from pykit import fsutil
from pykit.request import Request

if __name__ == '__main__':
    bucket_name = 'hu-by'
    key_name = 'hbykey'
    endpoint = 's2.lsl.com'

    # https://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPOST.html
    # Host must be in the format of destinationBucket.endpoint
    # you should add it in /etc/hosts
    host = bucket_name + '.' + endpoint
    port = 80

    access_key = 'u36vatc28bqy41oershl'
    secret_key = 'oTOZx9ONjXwOhqv6OMo1swa6eJECmf2d9xlqErdC'
    # send a post request
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
        'do_add_auth': True
    }
    request1 = Request(dict1)

    # upload a file
    fsutil.write_file('./hubiyong.txt', 'test upload a file')
    request1.content = open('./hubiyong.txt')
    request1.aws_sign(access_key, secret_key, request_date='20180918T120101Z')
    conn = http.Client(host, port)
    conn.send_request(request1['uri'], method='POST', headers=request1['headers'])
    conn.send_body(request1['body'])
    print conn.read_response()

    # send a put request
    file_content = "hby is testing sending put request"
    dict2 = {
        'verb': 'PUT',
        'uri': '/hu-by/test-key2',
        'args': {
                'foo2': 'bar2',
                'foo1': True,
                'foo3': ['bar3', True],
            },
        'headers': {
                'Host': host,
                'Content-Length': len(file_content),
            },
        'body': file_content,
        'fields': {},
        'do_add_auth': True
    }

    request2 = Request(dict2)
    request2.aws_sign(access_key, secret_key, sign_payload=True)
    conn = httplib.HTTPConnection(host, port)
    conn.request(request2['verb'], request2['uri'], request2['body'], request2['headers'])
    resp = conn.getresponse()
    print resp.status
    print resp.getheaders()
