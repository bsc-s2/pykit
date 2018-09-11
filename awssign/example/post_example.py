#!/usr/bin/env python2.6
# coding: utf-8

from pykit import awssign
from pykit import http
from pykit import httpmultipart


def send_post_request(host, port, headers, fields):
    conn = http.Client(host, port)
    multipart_cli = httpmultipart.Multipart()

    headers = multipart_cli.make_headers(fields, headers)
    body = multipart_cli.make_body_reader(fields)

    conn.send_request('/', method='POST', headers=headers)

    for data in body:
        conn.send_body(data)

    ret_status, ret_headers = conn.read_response()

    body = []
    while True:
        buf = conn.read_body(1024*1024)
        if buf == '':
            break

        body.append(buf)

    return {
        'status_code': ret_status,
        'headers': ret_headers,
        'body': ''.join(body),
    }


if __name__ == '__main__':
    bucket_name = 'your bucket name'
    key_name = 'key name to upload'
    endpoint = 's2 endpoint domain name'

    # https://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPOST.html
    # Host must be in the format of destinationBucket.endpoint
    # you should add it in /etc/hosts
    host = bucket_name + '.' + endpoint
    port = 80

    access_key = 'access key'
    secret_key = 'secret key'

    signer = awssign.Signer(access_key, secret_key)
    fields = {
        'key': key_name,  # key name
        'Policy': {
            'expiration': '2018-09-30T00:00:00.000Z',
            'conditions': [
                ['starts-with', '$key', ''],
                {
                    'bucket': bucket_name,  # bucket name
                },
            ],
        },
    }

    headers = {
        'Host': host,
    }

    signer.add_post_auth(fields, request_date='20180911T120101Z')

    fields_to_sent = []
    for k, v in fields.iteritems():
        fields_to_sent.append({'name': k, 'value': v})

    # file must be the last field
    # content can also be a opened file
    content = 'this is test of awssign.add_post_auth'
    fields_to_sent.append({
        'name': 'file',
        'value': [content, len(content), 'file name'],
    })

    print send_post_request(host, port, headers, fields_to_sent)
