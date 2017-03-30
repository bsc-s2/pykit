import os
import unittest

from pykit import net
from pykit import zkutil


class TestZKutil(unittest.TestCase):

    def test_lock_data(self):

        k = zkutil.lock_data('a')
        elts = k.split('-')

        self.assertEqual(3, len(elts))

        self.assertEqual('a', elts[0])
        self.assertTrue(net.is_ip4(elts[1]))
        self.assertEqual(os.getpid(), int(elts[2]))

    def test_parse_lock_data(self):

        cases = (
                ('', ('', None, None)),
                ('-', ('', '', None)),
                ('--', ('', '', None)),
                ('1-', ('1', '', None)),
                ('1-a', ('1', 'a', None)),
                ('1-a-x', ('1', 'a', None)),
                ('1-a-1', ('1', 'a', 1)),
        )

        for inp, expected in cases:

            rst = zkutil.parse_lock_data(inp)

            self.assertTrue(
                set(['node_id', 'ip', 'process_id']) == set(rst.keys()))
            self.assertEqual(
                expected, (rst['node_id'], rst['ip'], rst['process_id']))
