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

#   Status

The library is considered production ready.

#   Synopsis

Used to manage command. Set different arguments to execute different functions.

```
# set your commands in your source file: `demo.py`

from pykit import shell

arguments = {
    'echo_repr': (
                lambda x: sys.stdout.write(repr(x)),
                ('x', {'nargs': '+', 'help': 'just an input message'}),
            ),

    'foo': {
        'bar': lambda: sys.stdout.write('bar'),

        'bob': {
            'plus': (
                   lambda x, y: sys.stdout.write(str(x + y)),
                   ('x', {'type': int, help: 'an int is needed'}),
                   ('y', {'type': int, help: 'an int is needed'}),
                ),
        },
    },

    '__add_help__': {
        ('echo_repr',)           : 'output what is input.',
        ('foo', 'bar',)          : 'print a "bar".',
        ('foo', 'bob', 'plus',)  : 'do addition operation with 2 numbers.',
    },

    '__description__': 'this is an example command.',
}

shell.command(**arguments)

```
then you can execute your command as:
```
python demo.py echo_repr hello!
# 'hello!'

python demo.py foo bar
# 'bar'

python demo.py foo bob plus 1 2
# 3
```

and you can get a usage help message like:
```
$ python demo.py -h
---------------------------
usage: demo.py [-h] {echo_repr, foo bar, foo bob plus} ...

this is an example command.

positional arguments:
  {echo_repr, foo bar, foo bob plus} commands to select ...
    echo_repr            output what is input.
    foo bar              print a "bar".
    foo bob plus         do addition operation with 2 numbers.

optional arguments:
    -h, --help           show this help message and exit


$ python demo.py foo bob plus -h
--------------------------
usage: demo.py foo bob plus [-h] x y

positional arguments:
    x   an int is need
    y   an int is need

optional arguments:
    -h, --help           show this help message and exit
```


#   Description

A python module to manage commands.


#   Methods

##  shell.command

**syntax**:
`shell.command(**kwargs)`

**arguments**:

-  `kwargs`:
    A `dict` whose key is a `str`, used as a command, and value is a callable module, or another `dict`
    that has the same construction with `kwargs`.

    There are 2 optional reserved fields:

    -   `__add_help__`:
        A `dict` whose key is a tuple of commands path to the callable module in `kwargs`,
        and value is a string message.
        Set this key to add help messages for every callable value in `kwargs`.
        Then you can use `-h` option to get help message when running.

        If this key is setted, then you can add parameter help messages for every callable value like:
        `('x', {'nargs': 1, 'type'=int, help='an int is needed'})`,
        to make callable value as:

        ```
        (lamda x: do some thing with x,
          ('x', {'nargs': 1, 'type'=int, help='an int is needed'},
           ...
        )
        ```

        parameter help message is a `dict` and has the same format with key words arguments of
        `argparser.paser.add_argument`.

    -   `__description__`:
        Set this key to describe what `kwargs` can use to do.


#   Author

Wenbo Li(李文博) <wenbo.li@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Wenbo Li(李文博) <wenbo.li@baishancloud.com>
