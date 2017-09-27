<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
  - [colored string](#colored-string)
  - [colored command prompt](#colored-command-prompt)
- [Classes](#classes)
  - [strutil.ColoredString](#strutilcoloredstring)
- [Methods](#methods)
  - [strutil.break_line](#strutilbreak_line)
  - [strutil.color](#strutilcolor)
  - [strutil.colorize](#strutilcolorize)
  - [strutil.line_pad](#strutilline_pad)
  - [strutil.format_line](#strutilformat_line)
  - [strutil.struct_repr](#strutilstruct_repr)
  - [strutil.format_table](#strutilformat_table)
  - [strutil.tokenize](#strutiltokenize)
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

## colored string

```python
from pykit.strutil import blue
from pykit.strutil import green
blue("blue") + " and " + green("green")
```

The above snippet will output colored text on a terminal:

![](res/colored-string.png)

## colored command prompt

If you are going to use colored string as terminal prompt,
the terminal prompt is not wrapping correctly with very long commands.
You'd better tell **ColoredString** that is a prompt color string.

```python
from pykit.strutil import ColoredString
prompt = ColoredString('colored prompt# ', color='red', prompt=True)
```

Those screenshots show this issue, the cursor is box.

`prompt=False` long command:

![](res/colored-false-prompt.png)

`prompt=False` long command after **Home Key**:

![](res/colored-false-prompt-home-key.png)

`prompt=False` long command after **End Key**:

![](res/colored-false-prompt-end-key.png)

`prompt=True` long command:

![](res/colored-true-prompt.png)

`prompt=True` long command after **Home Key**:

![](res/colored-true-prompt-home-key.png)

`prompt=True` long command after **End Key**:

![](res/colored-true-prompt-end-key.png)

#   Classes

## strutil.ColoredString

**syntax**:
`strutil.ColoredString(normal_string, color=None, prompt=True)`

It provides the colored string in terminal on Unix.

**arguments**:

-   `normal_string`:
    the string to colour.

-   `color`:
    the color of **normal_string**,
    named color are:
    `blue` `cyan` `green` `purple` `red` `white` `yellow`
    `optimal` `normal` `loaded` `warn` `danger`,

    you can colour string with integer [0-256].

**return**:
An instance of strutil.ColoredString.


#   Methods


##  strutil.break_line

**syntax**:
`strutil.break_line(linestr, width)`

Split a string `linestr` to lines by one space or line break
to make length of every line no greater than `width`.
Only one space or line break is replaced at a time. Any others stay.

Examples:
```
strutil.break_line('foo bar bar.', 9)

#['foo bar', 'bar.']

print strutil.break_line('one   two  three', 4)

#['one ', ' two', '', 'three']
```

**arguments**:

-   `linestr`:
    is a string.

-   `width`:
    is the longest line length expected after being split.
    If `width` is negative, get the same result as `width` is 0.
    And if `width` is a float, just integer part is used.

**return**:
A list filled with lines of split `linestr`.

##  strutil.color

**syntax**:
`strutil.<color>(str)`

Create colored string to use in terminal.

```python
t = strutil.blue("blue-text")
```

Supported operation on colored string `t`:

```python
# concatenate with other colored string:
t + strutil.green("green-text")

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

## strutil.colorize

**syntax**:
`strutil.colorize(percent, total=100, ptn='{0}')`

Colorize a percentage number.

Synopsis:

```python
from pykit.strutil import colorize

# the color of p printed: blue -> green -> yellow -> red
for p in xrange(0, 100):
        print colorize(p, 100),
        print

# the color of p printed: red -> yellow -> green -> blue
for p in xrange(0, 100):
        print colorize(p, -100),
        print

# the color of p printed is red if p>=10
for p in xrange(0, 100):
        print colorize(p, 10),
        print

# the color of p printed is blue if p>=10
for p in xrange(0, 100):
        print colorize(p, -10),
        print

# 'the percent is: 100' with red
print colorize(100, 100, 'the percent is: {0}')

# ' 22%' with green
print colorize(22, 100, '{0:>3}%')
```

**arguments**:

-   `percent`:
    the percent to colour.

-   `total`:
    the limitation of **percent** to colour.
    negative integer means to reverse.

-   `ptn`:
    the format of **percent**.

**return**:
A colored formatted percent string.


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

##  strutil.struct_repr

**syntax**:
`strutil.struct_repr(d, key=None)`

Render primitive or composite data to a structural representation string
list.

```python
a = {
    1: 3,
    'x': {1:4, 2:5},
    'l': [1, 2, 3],
}
for l in strutil.struct_repr(a):
    print l

# 1 : 3
# l : - 1
#     - 2
#     - 3
# x : 1 : 4
#     2 : 5
```

**arguments**:

-   `d`:
    a number, string, list or dict to render to a structural
    representation.

-   `key`:
    is a callable that is used to sort dict keys.

    It is used in sort: `keys.sort(key=key)`.

**return**:
a list of string.

##  strutil.format_table

**syntax**:
`strutil.format_table(rows, keys=None, colors=None, row_sep=None, sep=' | ')`

Render a list of data into a table.

Number of rows is `len(rows)`.
Number of columns is `len(rows[0])`.


```python
inp = [
    {'acl': {},
     'bucket': 'game1.read',
     'bucket_id': '1400000000000689036',
     'num_used': '0',
     'owner': 'game1',
     'space_used': '0',
     'ts': '1492091893065708032'},
    {'acl': {},
     'bucket': 'game2.read',
     'bucket_id': '1510000000000689037',
     'num_used': '0',
     'owner': 'game2',
     'space_used': '0',
     'ts': '1492091906629786880'},
    {'acl': {'imgx': ['READ', 'READ_ACP', 'WRITE', 'WRITE_ACP']},
     'bucket': 'imgx-test',
     'bucket_id': '1910000000000689048',
     'num_used': '0',
     'owner': 'imgx',
     'space_used': '0',
     'ts': '1492101189213795840'}]

for l in strutil.format_table(inp, row_sep='-'):
    print l

# acl:               | bucket:    | bucket_id:          | num_used:  | owner:  | space_used:  | ts:
# -----------------------------------------------------------------------------------------------------------------
# {}                 | game1.read | 1400000000000689036 | 0          | game1   | 0            | 1492091893065708032
# -----------------------------------------------------------------------------------------------------------------
# {}                 | game2.read | 1510000000000689037 | 0          | game2   | 0            | 1492091906629786880
# -----------------------------------------------------------------------------------------------------------------
# imgx : - READ      | imgx-test  | 1910000000000689048 | 0          | imgx    | 0            | 1492101189213795840
#        - READ_ACP  |            |                     |            |         |              |
#        - WRITE     |            |                     |            |         |              |
#        - WRITE_ACP |            |                     |            |         |              |

# customize column header:
for l in strutil.format_table(inp, keys=[['bucket', 'Bkt'],
                                         ['num_used', 'n']]):
    print l

# Bkt:       | n:
# game1.read | 0
# game2.read | 0
# imgx-test  | 0
 ```

**arguments**:

-   `rows`:
    list of items to render.

    Element of list can be number, string, list or dict.

-   `keys`:
    specifies indexes(for list) or keys(for dict) to render.
    It is a list.

    Indexes or keys those are not in this list will not be rendered.

    It can also be used to specify customized column headers, if element in
    list is a 2-element tuple or list:

    ```
    keys = [
        ('bucket', 'Bkt'),
        ('num_used', 'n'),
        'bucket_id',
    ]
    # It output a talbe like below:
    # Bkt:       | n: | bucket_id:
    # game1.read | 0  | ...
    ```

-   `colors`:
    specifies the color for each column.
    It is a list of color values in number or color name strings.

    If length of `colors` is smaller than the number of columns(the number of
    indexes of a list, or keys of a dict), the colors are repeated for columns
    after.

-   `row_sep`:
    specifies char to separate rows.

    By default it is None, it means do not add line separator.

-   `sep`:
    specifies column separator char.

    By default it is `" | "`.

**return**:
a list of string.


## strutil.tokenize

**syntax**:
`strutil.tokenize(linestr, sep=None, quote='"\'', preserve=False)`

Tokenize a line.

Synopsis:

```python
from pykit.strutil import tokenize

# ['ab']
print tokenize('ab')

# ['a', 'b']
print tokenize('a b')

# ['a', 'b']
print tokenize(' a  b ')

# ['a', 'b']
print tokenize(' a\t b\n c\r ')

# ['a b', 'c d']
print tokenize('a bxyc d', sep='xy')

# ['a', 'x x', 'b']
print tokenize('a "x x" b')

# ['a', 'x x', 'b']
print tokenize("a 'x x' b 'x") # the last `'x` has no pair, discard

# ['a', 'a b', 'c d']
print tokenize(' a  xa bx yc dy ', quote='xy')

# ['a', 'xa bx', 'yc dy']
print tokenize('a xa bx yc dy', quote='xy', preserve=True)

# ['', 'a', 'xa bx', 'yc dy', '']
print tokenize(' a xa bx yc dy ', sep=' ', quote='xy', preserve=True)
```

**arguments**:

-   `linestr`:
    the line to tokenize.

-   `sep`:
    is None or a non-empty string separator to tokenize with.
    If sep is None, runs of consecutive whitespace are regarded as a single
    separator, and the result will contain no empty strings at the start or end
    if the string has leading or trailing whitespace. Consequently, splitting
    an empty string or a string consisting of just whitespace with a None
    separator returns `[]`. Just like `str.split(None)`.
    By default, `sep` is None.

-   `quote`:
    Every character in `quote` is regarded as a quote. Add a `\` prefix to make
    an exception. Segment between the same quotes is preserved.
    By default, `quote` is `'"\''`.

-   `preserve`:
    preserve the quote itself if `preserve` is `True`.
    By default, `preserve` is `False`.

**return**:
a list of string.

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
