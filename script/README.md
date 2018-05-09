<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Description](#description)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Description

-   `before-commit` is a wrapper of folowing 3 script to do static check,
    unittest and generate Table of content section of doc.

-   `pyauto` run static code check and reformat on python source code file.

    Usage:

    ```
    # check all *.py in current dir, recursively.
    $ pyauto

    # check one file:
    $ pyauto a.py
    ```

-   `t` run python built in unittest.

    `t` must be run in a module dir such as `humannum`.

    An optional argument can be used to specify what module/class/function to
    test:

    ```
    ./script/t
    ./script/t zkutil
    ./script/t zkutil.test
    ./script/t zkutil.test.test_zkutil
    ./script/t zkutil.test.test_zkutil.TestZKUtil
    ./script/t zkutil.test.test_zkutil.TestZKUtil.test_lock_data
    ```

    One can use `-v` to tell `t` to display verbose info during test:

    -   `t -v` lets python unittest run in verbose mode: to display each
        case function.

    -   `t -vv` or `t -v -v` enables displaying debug message by
        `pykit.ututil.dd()`.

    -   `t -C` to skip dependency check.
        If you are sure about dependency is complete, use `-C` to speed up test.

-   `toc` add Table-of-Content to markdown files.

    Usage:

    ```sh
    # build TOC for all *.md
    $ toc

    # build TOC for files:
    $ toc a.md b.md
    ```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
