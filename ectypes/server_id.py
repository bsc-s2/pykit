#!/usr/bin/env python2
# coding: utf-8

import re
import uuid


class ServerID(str):

    def __new__(clz, s):
        s = str(s)
        if re.match("^[0-9a-f]{12}$", s) is None:
            raise ValueError('ServerID must be 12 char hex, but: {s}'.format(s=s))

        return super(ServerID, clz).__new__(clz, s)

    @classmethod
    def local_server_id(self):
        return ServerID('%012x' % uuid.getnode())
