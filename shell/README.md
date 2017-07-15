<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [shell.command](#shellcommand)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

shell

# Status

The library is considered production ready.

#   Synopsis

Used to manage command. set diffent arguments to execute diffent functions.

```
# set your commands in your source file: `demo.py`

from pykit import shell

arguments = {
    'echo_repr': lambda *x: sys.stdout.write(repr(x)),

    'foo': {
        'bar': lambda *x: sys.stdout.write('bar'),

        'bob': {
            'alice': lambda *x: sys.stdout.write('alice'),
        },
    },
}

shell.command(**arguments)

```
then you can execute your command as:
```
python demo.py echo_repr hello!     # "('hello!',)" is printed
python demo.py foo bar              # 'bar' is printed
python demo.py foo bob alice        # 'alice' is printed
```

#   Description

A python module to manage commands.

#   Methods

##  shell.command

syntax:
`shell.command(**kwargs)`

arguments:

-  `kwargs`:
    A dict whose key is a command, and value is command option or function to run.

#   Author

Wenbo Li(李文博) <wenbo.li@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Wenbo Li(李文博) <wenbo.li@baishancloud.com>

