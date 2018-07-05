<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->  
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Methods](#methods)
  - [csvutil.to_dicts](#csvutilto_dicts)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Name

csvutil

# Status

This library is considered production ready.

# Description

Utility functions for CSV file loading and conversion.

#   Methods

## csvutil.to_dicts

**syntax**:
`csvutil.to_dicts(data, fields, on_invalid=None)`

Parsing a CSV file, each line of a CSV file corresponds to a dict.

```
xxx.csv 
123.5,xp,28
10,qq,30

to_dicts(d,[('ts', int), ('name', lambda s: s.upper()), 'age'])

output:
[
    {'ts': 123, 'name': 'XP', 'age': '28'},
    {'ts': 10, 'name': 'QQ', 'age': '30'}
]
```
**arguments**

-   `data`:
    Same as the first argument of CSV.DictReader.

    ```
    data = open('xxx.csv')
    ```

-   `fields`:
    Specify the name and type of each field in each row of data in CSV.


-   `on_invalid`:
    on_invalid(idx, field, val, exception):Callback function when parsing error.
    - idx: col number.
    - field: Is the field definition for idx passed in by to_dicts, for example ("name", to_upper).
    - val: The value of this field.
    - exception: Object that throws an exception.
-   `on_invalid`:
    If the value is None, an exception is thrown directly; if the value is 'ignore', it is ignored directly.

**return**:
    Returns an iterable, where each element is a dict, and each dict corresponds to a row in CSV.


#   Author

Cheng Yang (程洋) <yang.cheng@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2018 Cheng Yang(程洋) <yang.cheng@baishancloud.com>
