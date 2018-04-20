<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [utfyaml.dump](#utfyamldump)
  - [utfyaml.load](#utfyamlload)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

utfyaml: force `yaml.dump` and `yaml.load` in `utf-8` encoding.

#   Status

This library is considered production ready.

#   Synopsis

```
from pykit import utfyaml

utfyaml.load(
'''
key: value
number: 1
float: 3.14
boolean: True
汉字: 我
'''
)

#{
#   'key': 'value',
#   'number': 1,
#   'float': 3.14,
#   'boolean': True,
#   '汉字': '我',
#}

utfyaml.dump(
{
    'key': 'value',
    'number': 1,
    'float': 3.14,
    'boolean': True,
    '汉字': '我',
})

#'''
#key: value
#number: 1
#float: 3.14
#boolean': True
#汉字: 我
#'''

utfyaml.dump(
{
    'key': 'value',
    'number': 1,
    'float': 3.14,
    'boolean': True,
    '汉字': '我',
    u'unicode': 'hello, 中国',
}, encoding='GBK', save_unicode=True)

#"""
#key: value
#number: 1
#float: 3.14
#boolean: True
#\xba\xba\xd7\xd6: \xce\xd2
#!!python/unicode 'unicode': !!python/unicode 'hello, \xd6\xd0\xb9\xfa'
#"""
```

#   Description

Load a string with yaml format to a python instance in `utf-8` encoding
and dump a python instance to yaml format string in `utf-8` encoding.

#   Methods

##  utfyaml.dump

**syntax**:
`utfyaml.dump(py_instance, encoding='utf-8', save_unicode=False)`

Dump a python instance to a string with yaml format.

**arguments**:

-   `py_instance`:
    a python instance to be dumped to a yaml format string.

-   `encoding`:
    specifies in which encoding the result string is to be.
    By default, it is `'utf-8'`.
    If it is splecified and is `None`, means no need to encode
    and result string will be in `unicode`.

-   `save_unicode`:
    specifies if to dump `unicode` with tag `!!python/unicode`.
    By default, it is `False`.

**return**:
a string as the dump result of `py_instance` with yaml format.

##  utfyaml.load

**syntax**:
`utfyaml.load(yaml_string, encoding='utf-8')`

Load a string with yaml format to a python instance.

**arguments**:

-   `yaml_string`:
    a string with yaml format to be loaded to a python instance.

-   `encoding`:
    specifies in which encoding the strings in the result is to be.
    By default, it is `'utf-8'`.
    If it is specified and is `None`, means that no need to encode
    strings in the result, which will be in `unicode`.

**rerutn**:
the python instance `yaml_stirng` specified.

#   Author

Li Wenbo (李文博) <wenbo.li@baishancloud.com>


# Copyright and License

The MIT License (MIT)

Copyright (c) 2018 Li Wenbo (李文博) <wenbo.li@baishancloud.com>
