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
`utfjson.load(json_string)`

Load json string.

**arguments**:

-   `json_string`:
    a valid json string or `None`. If it is None, `utfjson.load` does not
    raise error, but returns None instead.

**return**:
the value parsed from `json_string`, it could be a `number`, `string`, `list`,
`dictionary` or `None`.

##  utfjson.dump

**syntax**:
`utfjson.dump(val)`

It dumps `val` to a json string the same way `json.dumps` does, except it
force string in `val` to be encoded in `utf-8`.

**arguments**:

-   `val`:
    a `number`, `string`, `list`, `dictionary` or `None`.

**return**:
json string

# Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

# Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
