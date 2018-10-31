#!/usr/bin/env python2
# coding: utf-8

import re
import uuid

from .idbase import IDBase
from .idc_id import IDCID
from .idc_id import IDC_ID_LEN

SERVER_ID_LEN = 12

def _mac_addr(s):
    s = str(s)
    if re.match("^[0-9a-f]{12}$", s) is None:
        raise ValueError('server id mac addr must be 12 char hex, but: {s}'.format(s=s))
    return s

class ServerID(IDBase):

    _attrs = (
            ('idc_id', 0, IDC_ID_LEN, IDCID), 
            ('mac_addr', IDC_ID_LEN, IDC_ID_LEN + SERVER_ID_LEN, _mac_addr),

            ('server_id', None, None, None, 'self'),
    )

    _str_len = IDC_ID_LEN + SERVER_ID_LEN

    _tostr_fmt = '{idc_id}{mac_addr}'

    @classmethod
    def local_server_id(self, idc_id):
        return ServerID(idc_id, '%012x' % uuid.getnode())
