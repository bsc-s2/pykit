<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [mime.get_by_filename](#mimeget_by_filename)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

mime

#   Status

The library is considered production ready.

#   Synopsis

```python
from pykit import mime

print mime.get_by_filename('file.json')
#  application/json
```

#   Description

This module provide some util methods to handle mime type.

#   Methods

##  mime.get_by_filename

**syntax**:
`mime.get_by_filename(filename)`

Return mime type according to filename suffix.

Examples:
```
print mime.get_by_filename('file.json')
#  application/json
```
**arguments**:

-   `filename`:
    is a string.

**return**:
mime type that predefined.

#   Author

Liu Tongwei(刘桐伟) <tongwei.liu@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Liu Tongwei(刘桐伟) <tongwei.liu@baishancloud.com>
