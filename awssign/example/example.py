#!/usr/bin/env python
# coding: utf-8

import time

from pykit import awssign

# to sign a request, you need to provide a dict which contain 'varb',
# 'uri', 'headers'
if __name__ == '__main__':
    access_key = 'your access key'
    secret_key = 'your secret key'

    # use query string
    request = {
        'verb': 'GET',
        'uri': '/aaa/b%20b?foo%2F&foo1=bar1%3F&foo2=bar2',
        'headers': {'Host': 'foo.bar.com'},
    }
    signer = awssign.Signer(access_key, secret_key)
    signer.add_auth(request)
    print request['uri']
    print request['headers']
    # > /aaa/b%20b?foo%2F&foo1=bar1%3F&foo2=bar2
    # > {'X-Amz-Content-SHA256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    #    'Host': 'foo.bar.com',
    #    'Authorization': 'AWS4-HMAC-SHA256 Credential=/20161208/us-east-1/s3/aws4_request, SignedHeaders=host;x-amz-date, Signature=0eefb35f051809e21f487499220ec7ed8243b0202f5ce6ab87fc177662d308de',
    #    ''X-Amz-Date': '20161208T113610Z'}

    # use args
    request = {
        'verb': 'GET',
        'uri': '/aaa/b%20b',
        'args': {'foo/': True, 'foo1': 'bar1?', 'foo2': 'bar2'},
        'headers': {'Host': 'foo.bar.com'},
    }
    signer = awssign.Signer(access_key, secret_key)
    signer.add_auth(request)
    print request['uri']
    print request['headers']
    # > /aaa/b%20b?foo%2F&foo1=bar1%3F&foo2=bar2
    # > {'X-Amz-Content-SHA256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    #    'Host': 'foo.bar.com',
    #    'Authorization': 'AWS4-HMAC-SHA256 Credential=/20161208/us-east-1/s3/aws4_request, SignedHeaders=host;x-amz-date, Signature=0eefb35f051809e21f487499220ec7ed8243b0202f5ce6ab87fc177662d308de',
    #    ''X-Amz-Date': '20161208T113610Z'}

    # query_auth
    request = {
        'verb': 'GET',
        'uri': '/aaa/bbb',
        'args': {'foo': ['bar1', 'bar2', True]},
        'headers': {'Host': 'foo.bar.com'},
    }
    signer = awssign.Signer(access_key, secret_key)
    signer.add_auth(request, query_auth=True)
    print request['uri']
    print request['headers']
    # > /aaa/bbb?foo=bar1&foo=bar2&foo&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Expires=60&X-Amz-Credential=your%20access%20key%2F20161208%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-SignedHeaders=host&X-Amz-Date=20161208T114712Z&X-Amz-Signature=58485ef2a476102e36fcd92a16894faaa81cfc95b200f83153f2fafa6c5e5200
    # > {'Host': 'foo.bar.com'}

    # use custom expires
    request = {
        'verb': 'GET',
        'uri': '/',
        'headers': {'Host': 'foo.bar.com'},
    }
    signer = awssign.Signer(access_key, secret_key)
    signer.add_auth(request, query_auth=True, expires=60 * 60 * 24)
    print request['uri']
    print request['headers']
    # > /?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Expires=86400&X-Amz-Credential=your%20access%20key%2F20161208%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-SignedHeaders=host&X-Amz-Date=20161208T115310Z&X-Amz-Signature=3baa1b0bfeffb9ddb8f41a5ef245eef63021c521d368364b4dee488c5eee71e8
    # > {'Host': 'foo.bar.com'}

    # sign payload
    request = {
        'verb': 'PUT',
        'uri': '/aaa/bbb',
        'headers': {'Host': 'foo.bar.com'},
        'body': 'bla bla'
    }
    signer = awssign.Signer(access_key, secret_key)
    signer.add_auth(request, sign_payload=True)
    print request['uri']
    print request['headers']
    # > /aaa/bbb
    # > {'X-Amz-Content-SHA256': 'fdcf4254fc02e5e41e545599f0be4f9f65e8be431ebc1fd301a96ea88dd0d5d6', 'Host': 'foo.bar.com', 'Authorization': 'AWS4-HMAC-SHA256 Credential=your access key/20161208/us-east-1/s3/aws4_request, SignedHeaders=host;x-amz-content-sha256;x-amz-date, Signature=97e72cd9e0e0cbb5b7db3477a4be3e463957433e7a2033f3e8b7c13456577c1e', 'X-Amz-Date': '20161208T115708Z'}

    # use custom request date
    future_time = time.time() + 60 * 60 * 24 * 365
    request = {
        'verb': 'GET',
        'uri': '/',
        'headers': {'Host': 'foo.bar.com'},
    }
    signer = awssign.Signer(access_key, secret_key)
    signer.add_auth(request, request_date=future_time)
    print request['uri']
    print request['headers']
    # > /
    # > {'X-Amz-Content-SHA256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Host': 'foo.bar.com', 'Authorization': 'AWS4-HMAC-SHA256 Credential=your access key/20171208/us-east-1/s3/aws4_request, SignedHeaders=host;x-amz-date, Signature=347d31c95bf94901f4bb36e7d5d0c2b60328759fc53d27ec3567229da62b7da8', 'X-Amz-Date': '20171208T120718Z'}

    # calculate the SHA256 of body by yourself
    from hashlib import sha256
    body = 'bla bla'
    digest = sha256(body).hexdigest()
    print digest
    request = {
        'verb': 'PUT',
        'uri': '/aaa/bbb',
        'headers': {'Host': 'foo.bar.com', 'X-Amz-Content-SHA256': digest},
    }
    signer = awssign.Signer(access_key, secret_key)
    signer.add_auth(request)
    print request['uri']
    print request['headers']
    # > fdcf4254fc02e5e41e545599f0be4f9f65e8be431ebc1fd301a96ea88dd0d5d6
    # > /aaa/bbb
    # > {'X-Amz-Content-SHA256': 'fdcf4254fc02e5e41e545599f0be4f9f65e8be431ebc1fd301a96ea88dd0d5d6', 'Host': 'foo.bar.com', 'Authorization': 'AWS4-HMAC-SHA256 Credential=your access key/20161208/us-east-1/s3/aws4_request, SignedHeaders=host;x-amz-date, Signature=2e3431de5980c3a90992e2e863a4e44f640bff9a425e0b71d9ebce7b17b0c006', 'X-Amz-Date': '20161208T122110Z'}

    # set headers not to be signed
    request = {
        'verb': 'PUT',
        'uri': '/aaa/bbb',
        'headers': {'Host': 'foo.bar.com',
                    'will-be-signed-h1': 'foo',
                    'will-not-be-signed-h1': 'foo',
                    'will-be-signed-h2': 'foo',
                    'will-not-be-signed-h2': 'foo', },
    }
    signer = awssign.Signer(access_key, secret_key)
    signer.add_auth(request, headers_not_to_sign=[
                    'will-not-be-signed-h1', 'will-not-be-signed-h2'])
    print request['uri']
    print request['headers']
    # > /aaa/bbb
    # > {'X-Amz-Content-SHA256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Host': 'foo.bar.com', 'will-not-be-signed-h1': 'foo', 'X-Amz-Date': '20161208T122416Z', 'will-not-be-signed-h2': 'foo', 'will-be-signed-h1': 'foo', 'will-be-signed-h2': 'foo', 'Authorization': 'AWS4-HMAC-SHA256 Credential=your access key/20161208/us-east-1/s3/aws4_request, SignedHeaders=host;will-be-signed-h1;will-be-signed-h2;x-amz-date, Signature=113428763e851f99a88e6439b3d38cc480df42a4524861b70306001db4edb266'}
