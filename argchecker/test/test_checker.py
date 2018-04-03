#!/usr/bin/env python2
# coding: utf-8

import os
import unittest

from pykit import argchecker


class TestChecker(unittest.TestCase):

    def test_check_arguments(self):
        cases = (
            (True, {'checker': {'type': 'bool'}}),
            (False, {'checker': {'type': 'bool'}}),

            (1, {'checker': {'type': 'integer'}}),
            (100, {'checker': {'type': 'integer'}}),

            (1, {'checker': {'type': 'float'}}),
            (50, {'checker': {'type': 'float'}}),
            (100.0, {'checker': {'type': 'float'}}),

            ('1', {'checker': {'type': 'string_number'}}),
            ('50', {'checker': {'type': 'string_number'}}),
            ('100.0', {'checker': {'type': 'string_number'}}),

            ('20', {'checker': {'type': 'string'}}),
            ('100.0', {'checker': {'type': 'string'}}),
            ('xxx', {'checker': {'type': 'string'}}),

            ([], {'checker': {'type': 'array'}}),
            ([1, 2], {'checker': {'type': 'array'}}),
            (['a', 'b'], {'checker': {'type': 'array'}}),

            ({'xx': {}}, {'xx': {'checker': {'type': 'dict'}}}),
            ({'xx': {'a': ''}}, {'xx': {'checker': {'type': 'dict'}}}),
        )

        for val, schema in cases:
            argchecker.check_arguments(val, schema)

    def test_required_arg(self):
        schema = {
            'x': {
                'checker': {'type': 'any'},
                'required': True
            }
        }
        with self.assertRaises(argchecker.LackArgumentError) as e:
            argchecker.check_arguments({}, schema)

        self.assertEqual(e.exception[0], 'x', "'x' is required")

    def test_undefined_arg(self):
        args = {'undefined': 0}
        schema = {'x': {'checker': {'type': 'any'}}}

        with self.assertRaises(argchecker.UnexpectedArgumentError) as e:
            argchecker.check_arguments(args, schema)

        self.assertEqual(e.exception[0], 'undefined')

    def test_float_arg(self):
        schema = {
            'num': {
                'required': True,
                'checker': {
                    'type': 'float',
                    'min': -100,
                    'max': 100,
                    'not': [0]
                }
            }
        }

        ex_cases = (
            ('1', argchecker.InvalidTypeError),
            (False, argchecker.InvalidTypeError),
            (-101, argchecker.OutOfRangeError),
            (101, argchecker.OutOfRangeError),
            (0, argchecker.InvalidValueError),
        )

        for val, err in ex_cases:
            self.assertRaises(err,
                              argchecker.check_arguments,
                              {'num': val},
                              schema)

        cases = (
            -100,
            -50,
            -10.88,
            50,
            99.99,
            100,
        )

        for val in cases:
            argchecker.check_arguments({'num': val}, schema)

    def test_integer_arg(self):
        schema = {
            'int': {
                'checker': {
                    'type': 'integer'
                }
            }
        }
        with self.assertRaises(argchecker.InvalidTypeError):
            argchecker.check_arguments({'int': 1.1}, schema)

        argchecker.check_arguments({'int': 100}, schema)

        long_num = 10 ** 21
        argchecker.check_arguments({'int': long_num}, schema)

    def test_string_number(self):
        schema = {
            'num': {
                'checker': {
                    'type': 'string_number',
                    'min': 0,
                    'max': 10,
                    'not': ['5'],
                }
            }
        }

        ex_cases = (
            (1, argchecker.InvalidTypeError),
            ('a', argchecker.InvalidTypeError),
            ('11', argchecker.OutOfRangeError),
            ('-1', argchecker.OutOfRangeError),
            ('5', argchecker.InvalidValueError),
        )

        for val, err in ex_cases:
            self.assertRaises(err,
                              argchecker.check_arguments,
                              {'num': val},
                              schema)

        cases = (
            '10',
            '0',
            '9.99',
            '4.30',
        )

        for val in cases:
            argchecker.check_arguments({'num': val}, schema)

    def test_string_and_string_number(self):
        schema = {
            'num': {
                'checker': [
                    {
                        'type': 'string_number'
                    },

                    {
                        'type': 'string',
                        'enum': ['auto']
                    }
                ]
            }
        }

        cases = (
            '123',
            'auto',
        )

        for val in cases:
            argchecker.check_arguments({'num': val}, schema)

    def test_fixed_len(self):
        str_schema = {
            'checker': {
                'type': 'string',
                'fixed_length': 3,
            },
        }

        array_schema = {
            'checker': {
                'type': 'array',
                'fixed_length': 3,
            },
        }

        dict_schema = {
            'xx': {
                'checker': {
                    'type': 'dict',
                    'fixed_length': 3,
                },
            }
        }

        cases = (
            ('abc', str_schema),
            (['a', 'b', 'abc'], array_schema),
            ({'xx': {'a': 'a', 'b': 'b', 'c': 'c'}}, dict_schema),
        )

        for v, s in cases:
            argchecker.check_arguments(v, s)

        ex_cases = (
            ('a', str_schema),
            ('ab', str_schema),
            ('abcd', str_schema),

            (['a'], array_schema),
            (['a', 'b'], array_schema),
            (['a', 'b', 'abc', 'abcd'], array_schema),

            ({'xx': {'a': ''}}, dict_schema),
            ({'xx': {'a': '', 'b': ''}}, dict_schema),
            ({'xx': {'a': '', 'b': '', 'c': '', 'd': ''}}, dict_schema),
        )

        for v, s in ex_cases:
            self.assertRaises(argchecker.InvalidLengthError,
                              argchecker.check_arguments,
                              v,
                              s)

    def test_min_max_len(self):
        str_schema = {
            'checker': {
                'type': 'string',
                'min_length': 2,
                'max_length': 4,
            }
        }

        array_schema = {
            'checker': {
                'type': 'array',
                'min_length': 2,
                'max_length': 4,
            }
        }

        dict_schema = {
            'xx': {
                'checker': {
                    'type': 'dict',
                    'min_length': 2,
                    'max_length': 4,
                }
            }
        }

        cases = (
            ('12', str_schema),
            ('123', str_schema),
            ('1234', str_schema),

            (['a', 'b'], array_schema),
            (['a', 'b', 'c'], array_schema),
            (['a', 'b', 'c', 'd'], array_schema),

            ({'xx': {'a': '', 'b': ''}}, dict_schema),
            ({'xx': {'a': '', 'b': '', 'c': ''}}, dict_schema),
            ({'xx': {'a': '', 'b': '', 'c': '', 'd': ''}}, dict_schema),
        )

        for v, s in cases:
            argchecker.check_arguments(v, s)

        ex_cases = (
            ('1', str_schema),
            ('12345', str_schema),

            (['a'], array_schema),
            (['a', 'b', 'c', 'd', 'e'], array_schema),

            ({'xx': {'a': ''}}, dict_schema),
            ({'xx': {'a': '', 'b': '', 'c': '', 'd': '', 'e': ''}}, dict_schema),
        )

        for v, s in ex_cases:
            self.assertRaises(argchecker.InvalidLengthError,
                              argchecker.check_arguments,
                              v,
                              s)

    def test_str_enum(self):
        enum = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                'Friday', 'Saturday', 'Sunday']
        schema = {
            'week_day': {
                'checker': {
                    'type': 'string',
                    'enum': enum,
                }
            }
        }

        ex_cases = (
            'xx',
            'foo',
            'bar',
            'today',
            'monday',
            'tUesday',
        )

        for c in ex_cases:
            self.assertRaises(argchecker.NotInEnumError,
                              argchecker.check_arguments,
                              {'week_day': c},
                              schema)

        for c in enum:
            argchecker.check_arguments({'week_day': c}, schema)

    def test_str_regexp(self):
        schema = {
            'alphabet_only': {
                'checker': {
                    'type': 'string',
                    'regexp': "^[a-z]+$"
                }
            }
        }

        with self.assertRaises(argchecker.PatternNotMatchError):
            argchecker.check_arguments({'alphabet_only': 'abcd123'}, schema)

        argchecker.check_arguments({'alphabet_only': 'abcd'}, schema)

    def test_array_arg(self):
        schema = {
            'numbers': {
                'checker': {
                    'type': 'array',
                    'element_checker': {
                        'type': 'integer'
                    }
                }
            }
        }
        with self.assertRaises(argchecker.InvalidTypeError):
            argchecker.check_arguments({'numbers': 123}, schema)

        with self.assertRaises(argchecker.InvalidTypeError):
            argchecker.check_arguments({'numbers': [1, 2, 'a']}, schema)

        argchecker.check_arguments({'numbers': []}, schema)
        argchecker.check_arguments({'numbers': [1, 2]}, schema)

    def test_dict_arg(self):
        schema = {
            'log_counter': {
                'checker': {
                    'type': 'dict',
                    'key_checker': {
                        'type': 'string',
                        'enum': ['info', 'error', 'warn']
                    },
                    'value_checker': {
                        'type': 'integer',
                        'min': 0
                    }
                }
            }
        }

        with self.assertRaises(argchecker.InvalidTypeError):
            argchecker.check_arguments({'log_counter': {1: 2}}, schema)

        with self.assertRaises(argchecker.NotInEnumError):
            argchecker.check_arguments({'log_counter': {'err': 1}}, schema)

        argchecker.check_arguments({'log_counter': {'error': 2, 'info': 1}},
                                   schema)

    def test_any_arg(self):
        schema = {
            'anything': {
                'checker': {'type': 'any'}
            }
        }
        for x in ([], {}, 0, ''):
            argchecker.check_arguments({'anything': x}, schema)

    def test_any_array(self):
        schema = {
            'anything': {
                'checker': {'type': 'array'}
            }
        }

        argchecker.check_arguments({'anything': [[], {}, 0, '']}, schema)

    def test_any_dict(self):
        schema = {
            'anything': {
                'checker': {'type': 'dict'}
            }
        }

        argchecker.check_arguments({'anything': {'1': 'a', 2: 'b', 3: [4]}}, schema)

    def test_nested_shema(self):
        sub_schema = {
            'nested_arg': {
                'checker': {'type': 'string'}
            }
        }
        schema = {
            'arg': {
                'checker': {
                    'type': 'dict',
                    'sub_schema': sub_schema
                }
            }
        }

        with self.assertRaises(argchecker.UnexpectedArgumentError) as e:
            argchecker.check_arguments({'arg': {'invalid_arg': '123'}}, schema)
        self.assertEqual(e.exception[0], 'invalid_arg')

        with self.assertRaises(argchecker.InvalidTypeError) as e:
            argchecker.check_arguments({'arg': {'nested_arg': 1}}, schema)
        self.assertEqual(e.exception[0], 'nested_arg')

        argchecker.check_arguments({'arg': {'nested_arg': '123'}}, schema)

    def test_checker_with_multi_types(self):
        schema = {
            'str_or_int': {
                'checker': [
                    {'type': 'string'},
                    {'type': 'integer'},
                ]
            }
        }

        cases = (
            'xx',
            123,
        )

        for val in cases:
            argchecker.check_arguments({'str_or_int': val}, schema)

        ex_cases = (
            [],
            (),
            {},
            0.1,
        )

        for val in ex_cases:
            self.assertRaises(argchecker.InvalidTypeError,
                              argchecker.check_arguments,
                              {'str_or_int': val},
                              schema)

    def test_read_schema(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_schema_path = test_dir + '/schema_example.yaml'
        schema = argchecker.read_schema(test_schema_path)

        self.assertIs(type(schema), dict)

    def _validate_and_assert_error_msg(self, schema, expected_err_msg):
        with self.assertRaises(argchecker.InvalidSchemaError) as e:
            argchecker.validate_schema({}, schema)

        self.assertIn(expected_err_msg, str(e.exception))

    def test_empty_schema(self):
        for schema in (None, {}):
            self._validate_and_assert_error_msg(schema, "Empty Schema")

    def test_missing_required_keyword(self):
        schema = {'arg': {}}
        expected_err_msg = "'checker' is required for scope 'root'"
        self._validate_and_assert_error_msg(schema, expected_err_msg)

        schema = {'arg': {'checker': {}}}
        expected_err_msg = "'type' is required for scope 'checker'"
        self._validate_and_assert_error_msg(schema, expected_err_msg)

    def test_extra_keyword(self):
        schema = {'arg': {'checker': {'type': 'float'},
                          'extra_keyword': True}}

        expected_err_msg = "'extra_keyword' is not a valid keyword"
        self._validate_and_assert_error_msg(schema, expected_err_msg)

    def test_invalid_keyword_type(self):
        schema = {'arg': {'checker': None}}
        expected_err_msg = "Expected types '['dict', 'array']' for 'checker', got 'None'"
        self._validate_and_assert_error_msg(schema, expected_err_msg)

        schema = {'arg': {'checker': {'type': 'float',
                                      'min': '0'}}}
        expected_err_msg = "Expected types '['float']' for 'min', got '0'"
        self._validate_and_assert_error_msg(schema, expected_err_msg)

        schema = {'arg': {'checker': {'type': 'float',
                                      'enum': [1, '2']}}}
        expected_err_msg = "Expected types '['float']' for 'enum', got '2'"
        self._validate_and_assert_error_msg(schema, expected_err_msg)

    def test_incorrect_keyword_scope(self):
        schema = {'arg': {'min': 0, 'checker': {'type': 'float'}}}
        expected_err_msg = "'min' is not in the correct scope "
        self._validate_and_assert_error_msg(schema, expected_err_msg)

    def test_invalid_scope_type(self):
        schema = {'arg': {'checker': {'type': 'array', 'min': 0}}}
        expected_err_msg = "'min' can only be used when the scope type is one of"
        self._validate_and_assert_error_msg(schema, expected_err_msg)

    def test_nested_checker(self):
        value_checker = {
            'type': 'array',
            'element_checker': {
                'type': 'string',
                'enum': [1, 2, 3]
            }
        }
        schema = {
            'arg': {
                'checker': {
                    'type': 'dict',
                    'value_checker': value_checker
                }
            }
        }

        expected_err_msg = "Expected types '['string']' for 'enum', got '1'"
        self._validate_and_assert_error_msg(schema, expected_err_msg)

    def test_nested_schema(self):
        sub_schema = {
            'sub_arg': {
                'checker': {'type': 'string'}
            }
        }
        schema = {
            'arg': {
                'checker': {
                    'type': 'dict',
                    'sub_schema': sub_schema
                }
            }
        }

        argchecker.validate_schema({}, schema)

    def test_checker_multi_types(self):
        schema = {
            'arg': {
                'checker': [
                    {'type': 'string', 'enum': ['auto']},
                    {'type': 'integer'}
                ]
            }
        }

        argchecker.validate_schema({}, schema)
