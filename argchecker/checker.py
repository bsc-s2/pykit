#!/usr/bin/env python2
# coding: utf-8

import errno
import re
import types
import yaml


cached_schemas = {}

BOOL = 'bool'
INTEGER = 'integer'
FLOAT = 'float'
STRING_NUMBER = 'string_number'
STRING = 'string'
ARRAY = 'array'
DICT = 'dict'
ANY = 'any'
# SCHEMA type should only be used by schema validator.
SCHEMA = 'schema'


TYPE_MAPPING = {
    BOOL: [types.BooleanType],
    INTEGER: [types.IntType, types.LongType],
    FLOAT: [types.IntType, types.LongType, types.FloatType],
    STRING_NUMBER: list(types.StringTypes),
    STRING: list(types.StringTypes),
    ARRAY: [types.ListType],
    DICT: [types.DictType],
    ANY: [types.BooleanType, types.IntType, types.LongType, types.FloatType,
          types.DictType, types.ListType] + list(types.StringTypes),

    SCHEMA: [types.DictType]
}

schema_keywords = {
    'checker': {
        'element_type': 'dict',
        'required': True,
        'scope': ['root', 'sub_schema'],
        'type': ['dict', 'array']
    },

    'element_checker': {
        'element_type': 'dict',
        'scope': ['checker', 'element_checker', 'value_checker'],
        'type': ['dict', 'array']
    },

    'enum': {
        'allowed_scope_types': ['string', 'integer', 'float', 'string_number'],
        'element_type': 'inherited',
        'scope': ['checker', 'element_checker', 'key_checker', 'value_checker'],
        'type': 'array'
    },

    'fixed_length': {
        'allowed_scope_types': ['string', 'array', 'dict'],
        'scope': ['checker', 'element_checker', 'key_checker', 'value_checker'],
        'type': 'integer'
    },

    'key_checker': {
        'element_type': 'dict',
        'scope': ['checker', 'element_checker', 'value_checker'],
        'type': ['dict', 'array']
    },

    'max': {
        'allowed_scope_types': ['integer', 'float', 'string_number'],
        'scope': ['checker', 'element_checker', 'key_checker', 'value_checker'],
        'type': 'float'
    },

    'max_length': {
        'allowed_scope_types': ['string', 'array', 'dict'],
        'scope': ['checker', 'element_checker', 'key_checker', 'value_checker'],
        'type': 'integer'
    },

    'min': {
        'allowed_scope_types': ['integer', 'float', 'string_number'],
        'scope': ['checker', 'element_checker', 'key_checker', 'value_checker'],
        'type': 'float'
    },

    'min_length': {
        'allowed_scope_types': ['string', 'array', 'dict'],
        'scope': ['checker', 'element_checker', 'key_checker', 'value_checker'],
        'type': 'integer'
    },

    'not': {
        'allowed_scope_types': ['string', 'integer', 'float', 'string_number'],
        'element_type': 'inherited',
        'scope': ['checker', 'element_checker', 'key_checker', 'value_checker'],
        'type': 'array'
    },

    'regexp': {
        'allowed_scope_types': ['string'],
        'scope': ['checker', 'element_checker', 'key_checker', 'value_checker'],
        'type': 'string'
    },

    'required': {
        'scope': ['root', 'sub_schema'],
        'type': 'bool'
    },

    'sub_schema': {
        'allowed_scope_types': ['dict'],
        'scope': ['checker', 'element_checker'],
        'type': 'schema'
    },

    'type': {
        'required': True,
        'scope': ['checker', 'element_checker', 'key_checker', 'value_checker'],
        'type': 'string'
    },

    'value_checker': {
        'element_type': 'dict',
        'scope': ['checker', 'element_checker', 'value_checker'],
        'type': ['dict', 'array']
    },
}


class SchemaCheckerError(Exception):
    pass


class SchemaNotFoundError(SchemaCheckerError):
    pass


class InvalidSchemaError(SchemaCheckerError):
    pass


class InvalidArgumentError(SchemaCheckerError):
    pass


class UnexpectedArgumentError(InvalidArgumentError):
    pass


class LackArgumentError(InvalidArgumentError):
    pass


class InvalidTypeError(InvalidArgumentError):
    pass


class OutOfRangeError(InvalidArgumentError):
    pass


class NotInEnumError(InvalidArgumentError):
    pass


class InvalidValueError(InvalidArgumentError):
    pass


class InvalidLengthError(InvalidArgumentError):
    pass


class PatternNotMatchError(InvalidArgumentError):
    pass


class ArgumentChecker(object):
    """
    Validate the argument based on the type definition in the schema.
    """

    any_checker = {'type': 'any'}

    def __init__(self, argument_name, value, checker):
        self.arg_name = argument_name
        self.val = value

        if type(checker) is list:
            checkers = checker
        else:
            checkers = [checker]

        self.checker = self.pick_checker_by_type(checkers)

    def pick_checker_by_type(self, checkers):
        checker_by_type = {c['type']: c for c in checkers}

        # Prefer string_number type if the val is a string number.
        if type(self.val) in TYPE_MAPPING['string']:
            if (_is_string_number(self.val) and
                    'string_number' in checker_by_type):
                return checker_by_type['string_number']

            elif 'string' in checker_by_type:
                return checker_by_type['string']

        for c in checkers:
            if type(self.val) in TYPE_MAPPING[c['type']]:
                return c

        types = [c['type'] for c in checkers]
        raise InvalidTypeError(self.arg_name, self.val, types)

    def check(self):
        func_name = 'check_{t}'.format(t=self.checker['type'])
        check_func = getattr(self, func_name)
        check_func()

    def _check_fixed_length(self):
        fixed_length = self.checker.get('fixed_length', None)
        if fixed_length is None:
            return

        if len(self.val) != fixed_length:
            raise InvalidLengthError(self.arg_name, self.val, fixed_length)

    def _check_length_range(self):
        min_len = self.checker.get('min_length', None)
        max_len = self.checker.get('max_length', None)
        val_len = len(self.val)

        if min_len is not None and val_len < min_len:
            raise InvalidLengthError(self.arg_name, self.val, min_len)

        if max_len is not None and val_len > max_len:
            raise InvalidLengthError(self.arg_name, self.val, max_len)

    def _check_length(self):
        self._check_fixed_length()
        self._check_length_range()

    def _check_invalid_values(self):
        invalid_vals = self.checker.get('not', None)
        if invalid_vals is None:
            return

        if self.val in invalid_vals:
            raise InvalidValueError(self.arg_name, self.val, invalid_vals)

    def _check_enums(self):
        enums = self.checker.get('enum', None)
        if enums is None:
            return

        if self.val not in enums:
            raise NotInEnumError(self.arg_name, self.val, enums)

    def _check_number_range(self):
        val = float(self.val)
        min_number = self.checker.get('min', None)
        max_number = self.checker.get('max', None)

        if min_number is not None and val < min_number:
            raise OutOfRangeError(self.arg_name, self.val, min_number)

        if max_number is not None and val > max_number:
            raise OutOfRangeError(self.arg_name, self.val, max_number)

    def _check_elements(self):
        elt_checker = self.checker.get('element_checker', None)
        if elt_checker is None:
            return

        for elt in self.val:
            elt_name = "{arg}'s element".format(arg=self.arg_name)
            ArgumentChecker(elt_name, elt, elt_checker).check()

    def _check_k_v(self):
        k_checker = self.checker.get('key_checker', None)
        v_checker = self.checker.get('value_checker', None)
        if k_checker is None and v_checker is None:
            return

        for k, v in self.val.iteritems():
            if k_checker is not None:
                k_name = "{arg}'s key".format(arg=self.arg_name)
                ArgumentChecker(k_name, k, k_checker).check()

            if v_checker is not None:
                v_name = "{arg}'s value".format(arg=self.arg_name)
                ArgumentChecker(v_name, v, v_checker).check()

    def _check_sub_schema(self):
        sub_schema = self.checker.get('sub_schema', None)
        if sub_schema is None:
            return

        check_arguments(self.val, sub_schema)

    def _check_regexp(self):
        regexp = self.checker.get('regexp')
        if regexp is None:
            return

        pattern = re.compile(regexp)
        if pattern.match(self.val) is None:
            raise PatternNotMatchError(self.arg_name, self.val, regexp)

    def check_any(self):
        pass

    def check_bool(self):
        pass

    def check_float(self):
        self._check_number_range()
        self._check_enums()
        self._check_invalid_values()

    def check_integer(self):
        self.check_float()

    def check_string_number(self):
        if not _is_string_number(self.val):
            raise InvalidTypeError(self.arg_name, self.val, ['string_number'])

        self.check_float()

    def check_string(self):
        self._check_enums()
        self._check_invalid_values()
        self._check_length()
        self._check_regexp()

    def check_array(self):
        self._check_length()
        self._check_elements()

    def check_dict(self):
        self._check_length()
        self._check_k_v()
        self._check_sub_schema()


def _is_string_number(val):
    try:
        float(val)
        return True
    except ValueError:
        return False


def _get_expected_types(keyword_type, scope_type):
    """
    Get the actual type of the keyword based on the defined keyword types, and
    the scope type that is only useful when the defined type is 'inherited'.
    """

    if keyword_type == 'inherited':
        assert scope_type is not None, ("Scope type should not be None "
                                        "when checking inherited value")
        return [scope_type]

    if type(keyword_type) is list:
        return keyword_type
    else:
        return [keyword_type]


def _validate_schema_in_scope(scope, schema):
    # Make sure required keywords exist.
    for keyword, definition in schema_keywords.iteritems():
        if (scope in definition['scope'] and definition.get('required') and
                keyword not in schema):
            raise InvalidSchemaError("'{k}' is required for scope '{s}'".
                                     format(k=keyword, s=scope))

    scope_type = schema.get('type')
    for keyword, val in schema.iteritems():
        if keyword not in schema_keywords:
            raise InvalidSchemaError("'{k}' is not a valid keyword".
                                     format(k=keyword))

        k_def = schema_keywords[keyword]
        if scope not in k_def['scope']:
            raise InvalidSchemaError("'{k}' is not in the correct scope {s}".
                                     format(k=keyword, s=k_def['scope']))

        allowed_scope_types = k_def.get('allowed_scope_types')
        if allowed_scope_types is not None and scope_type not in allowed_scope_types:
            raise InvalidSchemaError(
                "'{k}' can only be used when the scope type is one of {t}, "
                "got {real_t}".format(k=keyword, t=allowed_scope_types,
                                      real_t=scope_type))

        expected_types = _get_expected_types(k_def['type'], scope_type)
        _validate_type(scope_type, expected_types, keyword, val)


def _validate_type(scope_type, expected_types, keyword, val):
    """
    Validate the type of a keyword, and its sub keywords recursively.
    """
    keyword_type = None
    for t in expected_types:
        if type(val) in TYPE_MAPPING[t]:
            keyword_type = t
            break
    else:
        raise InvalidSchemaError("Expected types '{t}' for '{k}', got '{v}'".
                                 format(t=expected_types, k=keyword, v=val))

    if keyword_type == SCHEMA:
        # Validate sub schema.
        validate_schema({}, val)

    elif keyword_type == DICT:
        _validate_schema_in_scope(keyword, val)

    elif keyword_type == ARRAY:
        k_def = schema_keywords[keyword]
        expected_types = _get_expected_types(k_def['element_type'], scope_type)

        for element in val:
            _validate_type(scope_type, expected_types, keyword, element)


def validate_schema(args, schema):
    if schema is None or len(schema) == 0:
        raise InvalidSchemaError('Empty Schema')

    if not isinstance(args, dict):
        _validate_schema_in_scope('root', schema)
        return

    for _, schema in schema.iteritems():
        _validate_schema_in_scope('root', schema)


def read_schema(path):
    try:
        f = open(path)
    except IOError as e:
        if e.errno == errno.ENOENT:
            raise SchemaNotFoundError(path)
        else:
            raise

    content = f.read()

    try:
        return yaml.load(content)
    except yaml.error.YAMLError as e:
        raise InvalidSchemaError('{err} schema cannot be parsed'.format(
                                 err=repr(e)))


def check_arguments(args, schema):
    validate_schema(args, schema)

    if not isinstance(args, dict):
        ArgumentChecker('', args, schema['checker']).check()
        return

    for arg_name, sub_schema in schema.iteritems():
        if sub_schema.get('required', False) and arg_name not in args:
            raise LackArgumentError(arg_name)

    for arg_name, val in args.iteritems():
        if arg_name not in schema:
            raise UnexpectedArgumentError(arg_name, schema.keys())

        checker_schema = schema[arg_name]['checker']
        ArgumentChecker(arg_name, val, checker_schema).check()
