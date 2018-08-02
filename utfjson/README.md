<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [utfjson.load](#utfjsonload)
  - [utfjson.dump](#utfjsondump)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Name

utfjson: force `json.dump` and `json.load` in `utf-8` encoding.

# Status

This library is considered production ready.

#   Synopsis

```
from pykit import utfjson

utfjson.load('"hello"')
utfjson.dump({})
```

# Description

force `json.dump` and `json.load` in `utf-8` encoding.

#   Methods

## utfjson.load

**syntax**:
`utfjson.load(json_string, encoding=None)`

Load json string.

**arguments**:

-   `json_string`:
    a valid json string or `None`. If it is None, `utfjson.load` does not
    raise error, but returns None instead.

    `"\\x61"`(4 chars) is loaded into `'a'`(ascii 61).

-   `encoding`:
    specifies if to decode strings in result to unicode.

    Because there could be a string with uncertained encoding, by default it
    does not try to decode string.

    By default, with `encoding=None`:

    - `load('"\\u6211"')` results in a `unicode` string.

    - `load('"\xe6\x88\x91"')` results in a `str` string.

    If `encoding` is `"utf-8"`:

    - `load('"\xe6\x88\x91"')` results in a `unicode` string: `\u6211`.

**return**:
the value parsed from `json_string`, it could be a `number`, `string`, `list`,
`dictionary` or `None`.

##  utfjson.dump

**syntax**:
`utfjson.dump(val, encoding='utf-8', indent=None)`

It dumps `val` to a json string the same way `json.dumps` does, except it
force string in `val` to be encoded in `utf-8`.

**arguments**:

-   `val`:
    a `number`, `string`, `list`, `dictionary` or `None`.

-   `encoding`:
    specifies whether to encode unicode strings in `val`, before convert it to
    json.

    If `encoding` is `None`, it does not encode unicode strings.
    A unicode char will be converted to json directly.

    Following is an illustration of how `我` in `str` and `我` in `unicode` is
    handled by this `dump()`:

    > unicode of 我 is '\u6211', utf-8 encoded '我' is '\xe6\x88\x91'

    ```
    # expected behavior of dump('我'):
    #
    #           source             encoding=None  encoding='utf-8'
    # unicode  u'\u6211'           '"\\u6211"'    '"\xe6\x88\x91"'
    # str       '\xe6\x88\x91'     TypeError      '"\xe6\x88\x91"'
    ```
-   `indent`:
    a `number`, representing an indent in the returned json string

    If `indent` is `None`, it means no indentation is used

**return**:
json string

# Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

# Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
