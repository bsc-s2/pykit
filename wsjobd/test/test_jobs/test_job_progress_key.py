#!/usr/bin/env python2
# coding: utf-8

import logging
import time

logger = logging.getLogger(__name__)

def run( job ):

    data = job.data

    data['foo'] = '80%'

