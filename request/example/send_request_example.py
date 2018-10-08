#!/usr/bin/env python2
# coding: utf-8

from pykit import http
from pykit.request import Request

if __name__ == '__main__':
    bucket_name = 'your bucket name'
    key_name = 'key name to upload'
    endpoint = 's2 endpoint domain name'

    # https://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPOST.html
    # Host must be in the format of destinationBucket.endpoint
    # you should add it in /etc/hosts
    host = bucket_name + '.' + endpoint
    port = 80

    access_key = 'your access key'
    secret_key = 'your secret key'
    # send a post request
    dict1 = {
        'verb': 'POST',
        'uri': '/',
        'headers': {
            'Host': host,
        },
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
        'sign_args': {
            'access_key': access_key,
            'secret_key': secret_key,
            'request_date': '20180918T120101Z',
        }
    }

    request1 = Request(dict1, data=open('./xxx.txt'))

    conn = http.Client(host, port)
    conn.send_request(request1['uri'], method=request1['verb'], headers=request1['headers'])
    # request1['body'] is a generator object
    for body in request1['body']:
        conn.send_body(body)
    print conn.read_response()

    # send a put request
    file_content = "test sending put request"
    dict2 = {
        'verb': 'PUT',
        'uri': '/bucket_name/key_name',
        'args': {
                'foo2': 'bar2',
                'foo1': True,
                'foo3': ['bar3', True],
        },
        'headers': {
                'Host': host,
        },
        'sign_args': {
            'access_key': access_key,
            'secret_key': secret_key,
            'sign_payload': True,
        }
    }

    request2 = Request(dict2, data=file_content)

    conn = http.Client(host, port)
    conn.send_request(request2['uri'], method=request2['verb'], headers=request2['headers'])
    for body in request2['body']:
        conn.send_body(body)
    print conn.read_response
