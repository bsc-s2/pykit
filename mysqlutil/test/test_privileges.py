#!/usr/bin/env python
# coding: utf-8

import logging
import unittest

from pykit import mysqlutil
from pykit import ututil

dd = ututil.dd

logger = logging.getLogger(__name__)


class TestPrivileges(unittest.TestCase):

    def test_load_dump(self):
        ks = (
            "ALL",
            "ALTER",
            "ALTER ROUTINE",
            "CREATE",
            "CREATE ROUTINE",
            "CREATE TABLESPACE",
            "CREATE TEMPORARY TABLES",
            "CREATE USER",
            "CREATE VIEW",
            "DELETE",
            "DROP",
            "EVENT",
            "EXECUTE",
            "FILE",
            "GRANT OPTION",
            "INDEX",
            "INSERT",
            "LOCK TABLES",
            "PROCESS",
            "PROXY",
            "REFERENCES",
            "RELOAD",
            "REPLICATION CLIENT",
            "REPLICATION SLAVE",
            "SELECT",
            "SHOW DATABASES",
            "SHOW VIEW",
            "SHUTDOWN",
            "SUPER",
            "TRIGGER",
            "UPDATE",
            "USAGE",
        )

        for k in ks:
            self.assertEqual((k,), mysqlutil.privileges[k])
            self.assertEqual((k,), mysqlutil.privileges[k.replace(' ', '_')])

        shortcuts = {
            'replicator': (
                'REPLICATION CLIENT',
                'REPLICATION SLAVE',
                'SELECT',
            ),
            'monitor': (
                'SELECT',
            ),
            'business': (
                'CREATE',
                'DROP',
                'REFERENCES',
                'ALTER',
                'DELETE',
                'INDEX',
                'INSERT',
                'SELECT',
                'UPDATE',
            ),
            'readwrite': (
                'DELETE',
                'INSERT',
                'SELECT',
                'UPDATE',
            ),
        }

        for k, expected in shortcuts.items():
            self.assertEqual(expected, mysqlutil.privileges[k])
