import unittest
import os

from pykit import csvutil
from pykit import ututil

dd = ututil.dd


class TestToDicts(unittest.TestCase):

    dir_name = os.path.dirname(__file__)
    file_name = os.path.join(dir_name, 'test.csv')

    def test_right(self):

        cases_right = (

            (['id', 'name', 'add'],

             [{'id': '1',
               'name': 'cy',
               'add': 'bj'},
              {'id': '2',
               'name': '11',
               'add': 'xa'},
              {'id': '3',
               'name': 'mm',
               'add': '0x10'}]),

            ([('id', float,), 'name', 'add'],

             [{'id': 1.0,
               'name': 'cy',
               'add': 'bj'},
              {'id': 2.0,
               'name': '11',
               'add': 'xa'},
              {
               'id': 3.0,
               'name': 'mm',
               'add': '0x10'}]),

            (['id', 'name', ('add', lambda s: s.upper(),)],

                [{'id': '1',
                  'name': 'cy',
                  'add': 'BJ'},
                 {'id': '2',
                  'name': '11',
                  'add': 'XA'},
                 {'id': '3',
                  'name': 'mm',
                  'add': '0X10'}]),

        )

        for fields, out in cases_right:

            with open(self.file_name) as f:
                self.assertEqual(out, csvutil.to_dicts(f, fields))

    def test_exception(self):

        cases_exception = (

            (['id', 'name', ('add', int,)],
             ValueError,),

            (['id', 'name', ('add', lambda s: s+2,)],
             TypeError,),

            (['id', ('name', float,), 'add'],
             ValueError,),

            (['id', ('name', lambda s: s-1,), 'add'],
             TypeError,),

        )

        for fields, exception in cases_exception:

            with open(self.file_name) as f:
                self.assertRaises(exception, csvutil.to_dicts, f, fields)

    def test_ignore(self):

        cases_ignore = (

            (['id', ('name', int,), 'add'],
             'ignore',
             [{'id': '2',
               'name': 11,
               'add': 'xa'}]),

            (['id', 'name', ('add', int,)],
             'ignore',
             []),

            (['id', ('name', float,), 'add'],
             'ignore',
             [{'id': '2',
               'name': 11.0,
               'add': 'xa'}]),


        )

        for fields, callback, out in cases_ignore:

            with open(self.file_name) as f:
                self.assertEqual(out, csvutil.to_dicts(f, fields, callback))

    def test_on_invalid(self):

        list_on_invalid = []

        def on_invalid(idx, field, val, exception):
            list_on_invalid.append([idx, field, val, type(exception)])

        cases_on_invalid = (

            (['id', ('name', int,), 'add'],
             on_invalid,
             [[1, ('name', int,), 'cy', ValueError],
              [1, ('name', int,), 'mm', ValueError]]),

            ([('id', float,), ('name', float,), ('add', int)],
             on_invalid,
             [[1, ('name', float,), 'cy', ValueError],
              [2, ('add', int,), 'bj', ValueError],
              [2, ('add', int,), 'xa', ValueError],
              [1, ('name', float,), 'mm', ValueError],
              [2, ('add', int,), '0x10', ValueError]]),

        )

        for fields, callback, out in cases_on_invalid:

            with open(self.file_name) as f:
                csvutil.to_dicts(f, fields, on_invalid)

            self.assertEqual(out, list_on_invalid)

            del list_on_invalid[:]
