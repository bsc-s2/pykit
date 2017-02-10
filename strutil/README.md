<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
  - [colored string:](#colored-string)
- [Description](#description)
- [Methods](#methods)
  - [strutil.line_pad](#strutilline_pad)
  - [strutil.format_line](#strutilformat_line)
  - [strutil.color](#strutilcolor)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

strutil

It provides with several string operation functions.

#   Status

This library is considered production ready.

#   Synopsis

```python
from pykit import strutil

lines = [
    'hello',
    'world',
]

# add left padding to each line in a string
strutil.line_pad('\n'.join(lines), ' ' * 4)
# "    hello"
# "    world"


# format a multi-row line
items = [ 'name:',
          [ 'John',
            'j is my nick'
          ],

          'age:',
          26,

          'experience:',
          [ '2000 THU',
            '2006 sina',
            '2010 other'
          ],
]

strutil.format_line(items, sep=' | ', aligns = 'llllll')
# outputs:
#    name: | John         | age: | 26 | experience: | 2000 THU
#          | j is my nick |      |    |             | 2006 sina
#          |              |      |    |             | 2010 other
```

## colored string:

```python
from pykit.strutil import blue, green, yellow
blue("blue") + " and " + green("green")
```

The above snippet will output colored text on a terminal:

![](res/colored-string.png)

#   Description

It provides with several string operation functions.

#   Methods

## strutil.line_pad

**syntax**:
`strutil.line_pad(linestr, padding)`

**arguments**:

-   `linestr`:
    multiple line string with `\n` as line separator.

-   `padding`:
    left padding string to add before each line.

    It could also be a callable object that returns a string.
    This is useful when creating dynamic padding.

**return**:
multiple line string with `\n` as line separator, with left padding added.

## strutil.format_line

**syntax**:
`strutil.format_line(elts, sep=' ', aligns='')`

It formats a list in a multi row manner.

It is compatible with colored string such as those created with `strutil.blue("blue-text")`.

```python
strutil.format_line([1, "a:", "b"], sep=" | ")
# "1 | a: | b"

strutil.format_line([["name:", "age:"], ["drdrxp", "18"], "wow"], sep=" | ", aligns="rll")
# "name: | drdrxp | wow"
# " age: | 18     |"
```

**arguments**:

-   `elts`:
    elements in a line.
    Each element could be a `string` or a `list` of `string`.
    If it is a `list` of `string`, it would be rendered as a multi-row
    element.

-   `sep`:
    specifies the separator between each element in a line.
    By default it is a single space `" "`.

-   `aligns`:
    specifies alignment for each element.
    -   `l` for left-align.
    -   `r` for right-align.

    If no alignment specified for i-th element, it will be aligned to right by
    default.

**return**:
formatted string.

##  strutil.color

**syntax**:
`strutil.<color>(str)`

Create colored string for use in terminal.

```python
t = strutil.blue("blue-text")
```

Supported operation on colored string `t`:

```python
# concatenate with plain string:
t + "a"

# repeat:
t * 3

# length:
len(t)
```

Supported color names:

-   `blue`
-   `cyan`
-   `green`
-   `yellow`
-   `red`
-   `purple`
-   `white`
-   `optimal` same as `blue`
-   `normal` no color
-   `loaded` same as `green`
-   `warn` same as `dark yellow`
-   `danger` same as `red`

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
