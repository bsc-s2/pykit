<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Install](#install)
- [Usage](#usage)
- [Update sub repo](#update-sub-repo)
- [Methods](#methods)
  - [init](#init)
  - [add_auth](#add-auth)
  - [add_post_auth](#add-post-auth)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

awssign:
A python lib used for signing a request using aws signature version 4

#   Status

This library is in beta phase.

It has been used heavily in our object storage service, as a foundamental
library of our devops platform.

#   Description

This lib is used to sign a request using aws signature vesrion 4. You
need to provide a python dict which represent your request(it typically
contains `verb`, `uri`, `args`, `headers`, `body`), and you access key
and you secret key. This lib will add signatrue to the request.

#   Install

This package does not support installation.

Just clone it and copy it into your project source folder.

```
cd your_project_folder
git clone https://github.com/baishancloud/awssign.git
```

#   Usage

```python
import awssign
import httplib

access_key = 'your access key'
secret_key = 'your secret key'

signer = awssign.Signer(access_key, secret_key)

file_content = 'bla bla'
request = {
    'verb': 'PUT',
    'uri': '/test-bucket/test-key',
    'args': {
        'foo2': 'bar2',
        'foo1': True,
        'foo3': ['bar3', True],
    },
    'headers': {
        'Host': 'bscstorage.com',
        'Content-Length': len(file_content),
    },
    'body': file_content,
}

signer.add_auth(request, sign_payload=True)

conn = httplib.HTTPConnection('bscstorage.com')
conn.request(request['verb'], request['uri'], request['body'], request['headers'])
resp = conn.getresponse()
```

#  Update sub repo

>   You do not need to read this chapter if you are not a maintainer.

First update sub repo config file `.gitsubrepo`
and run `git-subrepo`.

`git-subrepo` will fetch new changes from all sub repos and merge them into
current branch `mater`:

```
./script/git-subrepo/git-subrepo
```

`git-subrepo` is a tool in shell script.
It merges sub git repo into the parent git working dir with `git-submerge`.

#   Methods

##  init

The initiate method of class `Signer`.

### prototype

```python
Singer.__init__(self, access_key, secret_key, region=None, service=None, default_expires=None)
```

### arguments

It receive the following arguments:

- `access_key` is the access key used to sign the request.

- `secret_key` is the secret key used to sign the request.

- `region` is the region name of the service, the default is 'us-east-1'.

- `serive` is service name, the default is 's3'.

- `default_expires` is the default expires time of a presigned url in seconds,
    the default is 60.

##  add-auth

The method used to sign a request.

### prototype

```
add_auth(self, request, **argkv)
```

### arguments

It receives the following arguments:

- `request` is a python dict which represent your request.
    It may contents the following keys:

    - `verb` is the request method, such as 'GET', 'PUT'.

    - `uri` is the url encoded uri, it can contains query string if you did not
        include `args` in `request`.

    - `args` is a python dict contains the request parameters, it should not be
        url encoded. You can not use both `args` and query string in `uri` in the
        same `request`.

    - `headers` is a python dict contains request headers. It must contains the
        'Host' header.

    - `body` is a string, contains the request payload. If you do not want to sign
       the payload or you have set 'X-Amz-ContentSHA256' header in `headers`, you
       can omit this key.

- `argkv` is a dict contains some optional arguments.
    It can contains the following arguments:

    - `query_auth` is a boolean value to indicate whether the signature should be add
        to query string.

    - `sign_payload` is a boolean value to indicate whether the payload should be signed.

    - `headers_not_to_sign` is a list of header names, to indicate which headers are
        not need to be signed.

    - `request_date` is a timestamp or a iso base format date string, used to specify
        a custom request date, instead of using current time as request date.

    - `expires` is number seconds to indicate how long will a presigned url be valid.
        It will overwrite the value of `default_expires`.

    - `signing_date` is a 8 digital date string like '20170131', used to specify a
        custom signing date.

##  add-post-auth

The method used to sign a browser based post request.

### prototype

```
add_post_auth(self, fields, **argkv)
```

### arguments

It receives the following arguments:

- `fields` is a python dict which contains form fields.
    It may contents the following keys:

    - `Policy` is python dict, describing what is permitted in the request.
        after this function call, it will be replaced by it's base64 encoded
        version.

    - `key` the key of the object to upload.

    It also support some other fields, more infomation at
    [here](http://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPOST.html)
    This method will add some signature related fields to this dict.

#   Author

Renzhi (任稚) <zhi.ren@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2016 Renzhi (任稚) <zhi.ren@baishancloud.com>
