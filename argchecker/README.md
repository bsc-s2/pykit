<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Argument Schema](#argument-schema)
- [Keywords](#keywords)
  - [required](#required)
  - [checker](#checker)
- [Checker Keywords](#checker-keywords)
  - [type](#type)
  - [min](#min)
  - [max](#max)
  - [fixed_length](#fixed_length)
  - [min_length](#min_length)
  - [max_length](#max_length)
  - [enum](#enum)
  - [not](#not)
  - [regexp](#regexp)
  - [element_checker](#element_checker)
  - [key_checker](#key_checker)
  - [value_checker](#value_checker)
  - [sub_schema](#sub_schema)
- [Exceptions](#exceptions)
  - [argchecker.SchemaCheckerError](#argcheckerschemacheckererror)
  - [argchecker.SchemaNotFoundError](#argcheckerschemanotfounderror)
  - [argchecker.InvalidSchemaError](#argcheckerinvalidschemaerror)
  - [argchecker.InvalidArgumentError](#argcheckerinvalidargumenterror)
  - [argchecker.UnexpectedArgumentError](#argcheckerunexpectedargumenterror)
  - [argchecker.LackArgumentError](#argcheckerlackargumenterror)
  - [argchecker.InvalidTypeError](#argcheckerinvalidtypeerror)
  - [argchecker.OutOfRangeError](#argcheckeroutofrangeerror)
  - [argchecker.NotInEnumError](#argcheckernotinenumerror)
  - [argchecker.InvalidValueError](#argcheckerinvalidvalueerror)
  - [argchecker.InvalidLengthError](#argcheckerinvalidlengtherror)
  - [argchecker.PatternNotMatchError](#argcheckerpatternnotmatcherror)
- [Methods](#methods)
  - [argchecker.validate_schema](#argcheckervalidate_schema)
  - [argchecker.read_schema](#argcheckerread_schema)
  - [argchecker.check_arguments](#argcheckercheck_arguments)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

argchecker

# Status

The library is considered production ready.

#   Synopsis

```
# MathTask.yaml
x:
  checker:
    type: float
    min: -100
    max: 100
  required: true

y:
  checker:
    type: float
    not: 0
  required: true

op:
  checker:
    type: string
    enum:
      - add
      - sub
      - multiply
      - divide
  required: false
```

Makes sure a schema is valid.

```
from pykit import argchecker

schema = {
    'checker': {
        'type': 'string',
        'min_length': 'bar',
    }
}

try:
    argchecker.validate_schema('foo', schema)

except argchecker.InvalidSchemaError as e:
    print(repr(e) + ' invalid schema')
```

Validates arguments against the schema.

```
from pykit import argchecker

# schema.yaml
# x:
#   checker:
#     type: string

schema = argchecker.read_schema('/path/to/schema.yaml')
try:
    argchecker.check_arguments({'x': 'auto'}, schema)

except argchecker.SchemaCheckerError as e:
    print(repr(e) + ' invalid arguments')
```

#   Description

Validates arguments against the schema.
Raise a exception(subclass of `SchemaCheckerError`) if they are mismatched.

Support types:
```
'bool'
'integer'
'float'
'string_number'
'string'
'array'
'dict'
```

#   Argument Schema

A schema file is written in YAML and consists a dictionary mapping
from the argument name to its definition with keywords.

```
arg_1:
  key_word1: ...
  key_word2: ...

arg_2:
  key_words: ...
```

#   Keywords

##  required

Whether a argument is required.

**Values**：`(true, false)`

**Default**：`false`


## checker

Define a valid argument with sub keywords, such as `type`, `min`, `max`, etc.
**(required keyword)**

**Value Type**：Dictionary or List of dictionary。

```
checker:
  type: float
  min: 0
  max: 100
```

Set the checker with a list of dictionary if the argument can have multiple types.

For example:

```
Resolution:
  checker:
    - type: string
      enum: ['auto']
    - type: integer
      min: 320
      max: 1080
```

#   Checker Keywords

##  type

Define the type of the keyword's value. **(required keyword)**

**Values**：`[bool, integer, float, string, array, dict, any]`.

- `bool`: true or false.

- `integer`: an integer number.

- `float`: a floating number, includes integer.

- `string_number`: a number with string type.

- `string`: a string.

- `array`: an array.

- `dict`: a K/V dictionary.

- `any`: any of the above. **(not recommended)**

##  min

Define the minimum value of a number.
**(left closed)**

**Suitable Types**: `[integer, float, string_number]`

**Values**: any number

```
x:
  checker:
    type: integer
    min: 100

y:
  checker:
    type: float
    min: 100

z:
  checker:
    type: string_number
    min: 100
```

##  max

Define the maximum value of a number.
**(right closed)**

**Suitable Types**: `[integer, float, string_number]`

**Values**: any number

```
x:
  checker:
    type: integer
    max: 100

y:
  checker:
    type: float
    max: 100

z:
  checker:
    type: string_number
    max: 100
```

##  fixed_length

Define the length of an argument.

**Suitable Types**: `[string, array, dict]`

**Values**: any integer.

```
x:
  checker:
    type: string
    fixed_length: 10

y:
  checker:
    type: array
    fixed_length: 10

z:
  checker:
    type: dict
    fixed_length: 10
```

##  min_length

Define the minimum length of an argument.
**(left closed)**

**Suitable Types**: `[string, array, dict]`

**Values**：an integer

```
x:
  checker:
    type: string
    min_length: 10

y:
  checker:
    type: array
    min_length: 10

z:
  checker:
    type: dict
    min_length: 10
```

##  max_length

Define the maximum length of an argument.
**(right closed)**

**Suitable Types**: `[string, array, dict]`

**Values**：an integer.

```
x:
  checker:
    type: string
    max_length: 10

y:
  checker:
    type: array
    max_length: 10

z:
  checker:
    type: dict
    max_length: 10
```

##  enum

Define the valid values of an argument.

**Suitable Types**: `[string, integer, float, string_number]`

**Values**：an array of elements whose type should be the same as the checker type.

```
op:
  checker:
    type: string
    enum: [add, sub, multiply, divide]
```

NOTE: This is case sensitive。

##  not

Define the invalid values of an argument.

**Suitable Types**: `[string, integer, float, string_number]`

**Values**: an array of elements whose type should be the same as the checker type。


```
country:
  checker:
    type: string
    not: [US, Japan]
```

NOTE: This is case sensitive。

##  regexp

The regular expression used to validate an argument.

**Suitable Types**: `[string]`

**Values**: a string。

NOTE: please make sure the regular expression you set is valid.

```
x:
  checker:
    type: string
    regexp: "^[a-z]+$"
```

##  element_checker

Define the type and detail of the elements of an array.

**Suitable Types**: `[array]`

**Values**: a checker dictionary

**Default Value**: any

```
numbers:
  checker:
    type: array
    element_checker:
      type: integer
      min: 0
```

##  key_checker

Define the type and detail of the keys of a dictionary.

**Suitable Types**: `[dict]`

**Values**: a checker dictionary

**Default Value**: any

##  value_checker

Define the type and detail of the values of a dictionary.

**Suitable Types**: `[dict]`

**Values**: a checker dictionary

**Default Value**: any

```
log_counter:
  checker:
    type: dict
    key_checker:
      type: string
      enum: [info, warn, error]
    value_checker:
      type: integer
      min: 0
```

##  sub_schema

A nested schema used to define the keys and values of a dictionary argument.

**Suitable Types**: `[dict]`

**Values**: same as a schema

```
video:
  checker:
    type: dict
    sub_schema:
      height:
        checker:
          type: integer
          min: 0
      width:
        checker:
          type: integer
          min: 0
```

#   Exceptions

##  argchecker.SchemaCheckerError

**syntax**:
`argchecker.SchemaCheckerError`

The base class of the other exceptions in this module.
It is a subclass of `Exception`.

##  argchecker.SchemaNotFoundError

**syntax**:
`argchecker.SchemaNotFoundError`

A subclass of `SchemaCheckerError`.
Raise if the provided YAML file don't exist.

##  argchecker.InvalidSchemaError

**syntax**:
`argchecker.InvalidSchemaError`

A subclass of `SchemaCheckerError`.
Raise if the provided schema is invalid.

##  argchecker.InvalidArgumentError

**syntax**:
`argchecker.InvalidArgumentError`

A subclass of `SchemaCheckerError`.
Raise if the schema and arguments are mismatched.

##  argchecker.UnexpectedArgumentError

**syntax**:
`argchecker.UnexpectedArgumentError`

A subclass of `InvalidArgumentError`.
Raise if the key of the arguments is not in schema.

```
from pykit import argchecker

# schema.yaml
# x:
#   checker:
#     type: string

schema = argchecker.read_schema('/path/to/schema.yaml')
argchecker.check_arguments({'y': 'auto'}, schema)
# 'y' is in the arguments, but not in the schema.
# in this case, it will raise a 'UnexpectedArgumentError'
```

##  argchecker.LackArgumentError

**syntax**:
`argchecker.LackArgumentError`

A subclass of `InvalidArgumentError`.
Raise if the required key not in the arguments.

```
from pykit import argchecker

# schema.yaml
# x:
#   checker:
#     type: string
#   required: true
# y:
#   checker:
#     type: string

schema = argchecker.read_schema('/path/to/schema.yaml')
argchecker.check_arguments({'y': 'auto'}, schema)
# 'x' is required in the arguments.
# 'y' is optional in the arguments.
# in this case, it will raise a 'LackArgumentError',
# becase of 'x' not in the arguments.
```

##  argchecker.InvalidTypeError

**syntax**:
`argchecker.InvalidTypeError`

A subclass of `InvalidArgumentError`.
Raise if type of checker is invalid.

```
from pykit import argchecker

# schema.yaml
# x:
#   checker:
#     type: foo

schema = argchecker.read_schema('/path/to/schema.yaml')
argchecker.check_arguments({'x': 'auto'}, schema)
# the type 'foo' is invalid.
# in this case, it will raise a 'InvalidTypeError'.
```

##  argchecker.OutOfRangeError

**syntax**:
`argchecker.OutOfRangeError`

A subclass of `InvalidArgumentError`.
Raise if the argument is out of range.

```
from pykit import argchecker

# schema.yaml
# x:
#   checker:
#     type: integer
#     min: 1
#     max: 100

schema = argchecker.read_schema('/path/to/schema.yaml')
argchecker.check_arguments({'x': 1000}, schema)
# the range is [1, 100], so 1000 is out of range.
# in this case, it will raise a 'OutOfRangeError'.
```

##  argchecker.NotInEnumError

**syntax**:
`argchecker.NotInEnumError`

A subclass of `InvalidArgumentError`.
Raise if the argument is not in the provided `enum` values.

```
from pykit import argchecker

# schema.yaml
#x:
#  checker:
#    type: string
#    enum:
#      - add
#      - sub

schema = argchecker.read_schema('/path/to/schema.yaml')
argchecker.check_arguments({'x': 'xx'}, schema)
# 'xx' is not in the provided values.
# in this case, it will raise a 'NotInEnumError'.
```

##  argchecker.InvalidValueError

**syntax**:
`argchecker.InvalidValueError`

A subclass of `InvalidArgumentError`.
Raise if the argument is in the provided `not` values.

```
from pykit import argchecker

# schema.yaml
#x:
#  checker:
#    type: string
#    not: ['foo', 'bar']

schema = argchecker.read_schema('/path/to/schema.yaml')
argchecker.check_arguments({'x': 'foo'}, schema)
# 'foo' is in the invalid values.
# in this case, it will raise a 'InvalidValueError'.
```

##  argchecker.InvalidLengthError

**syntax**:
`argchecker.InvalidLengthError`

A subclass of `InvalidArgumentError`.
Raise if length of the argument(`string`,`dict`,`array`) is invalid.

```
from pykit import argchecker

# schema.yaml
#x:
#  checker:
#    type: string
#    fixed_length: 1

schema = argchecker.read_schema('/path/to/schema.yaml')
argchecker.check_arguments({'x': 'foo'}, schema)
# length of 'x' is invalid.
# in this case, it will raise a 'InvalidLengthError'.
```

##  argchecker.PatternNotMatchError

**syntax**:
`argchecker.PatternNotMatchError`

A subclass of `InvalidArgumentError`.
Raise if the value and the regexp are mismatched.
Only used for `string` type.

```
from pykit import argchecker

# schema.yaml
#x:
#  checker:
#    type: string
#    regexp: "^[a-z]+$"

schema = argchecker.read_schema('/path/to/schema.yaml')
argchecker.check_arguments({'x': '123foo'}, schema)
# '123foo' and the '^[a-z]+$' are mismatched.
# in this case, it will raise a 'PatternNotMatchError'.
```

#   Methods

##  argchecker.validate_schema

**syntax**:
`argchecker.validate_schema(args, schema)`

Makes sure a schema is valid.
Raise a `InvalidSchemaError` if the schema is invalid.

**arguments**:

-   `args`:
    the arguments that need to be checked. Type of it must be
    in `[bool, integer, float, string, array, dict, any]`.

-   `schema`:
    it is a `dict`.It consists a dictionary mapping from
    the argument name to its definition with keywords.

**return**:
nothing

##  argchecker.read_schema

**syntax**:
`argchecker.read_schema(path)`

Read a YAML file and convert the content to a `dict`.
Raise a `SchemaNotFoundError` if the file don't exist.

**arguments**:

-   `path`:
    it is a `str`, the path of the YAML file.

**return**:
a `dict`. The content of the YAML file.

```
from pykit import argchecker
# test.yaml
#x:
#  checker:
#    type: string

schema = argchecker.read_schema('test.yaml')
```

##  argchecker.check_arguments

**syntax**:
`argchecker.check_arguments(args, schema)`

Validates arguments against the schema.
Raise a `InvalidSchemaError` if `schema` is invalid.
Raise a `InvalidArgumentError` if `args` and `schema` are mismatched.

```
from pykit import argchecker

# check a dict
schema = {
    x:{
        'checker': {
            'type': 'string',
            'min_length': 10,
        },

        'required': True,
    },

    y:{
        'checker': {
            'type': 'integer',
            'min': 10,
        },

        'required': True,
    }
}

try:
    argchecker.check_arguments({'x': 'foo', 'y': 8}, schema)

except argchecker.SchemaCheckerError as e:
    print(repr(e) + ' check failed')

# check a string
schema = {
    'checker': {
        'type': 'string',
        'min_length': 10,
    },
}

try:
    argchecker.check_arguments('foobar', schema)

except argchecker.SchemaCheckerError as e:
    print(repr(e) + ' check failed')
```

**arguments**:

-   `args`:
    the arguments that need to be checked. Type of it must be
    in `[bool, integer, float, string, array, dict, any]`.

-   `schema`:
    it is a `dict`.It consists a dictionary mapping from
    the argument name to its definition with keywords.

**return**:
nothing
