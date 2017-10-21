#!/usr/bin/env python2
# coding: utf-8

import json
import mimetypes
import os

OCTET_STREAM = 'application/octet-stream'

dir_name = os.path.dirname(__file__)
resource = os.path.join(dir_name, 'thirdpart', 'mimes.json')


def _init():
    with open(resource, 'r') as f:
        content = f.read()
    return json.loads(content)


mimes = _init()


def get_by_filename(filename):
    mime_type = None

    if filename.find('.') != -1:
        suffix = filename.rsplit('.', 1)[-1]
        mime_type = mimes.get(suffix)
        if mime_type is None:
            mime_type, _ = mimetypes.guess_type(filename)

    return mime_type or OCTET_STREAM
