<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Description](#description)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Description

-   `pyauto.sh` run static code check and reformat on python source code file.

    Usage:

    ```
    # check all *.py in current dir, recursively.
    $ pyauto.sh

    # check one file:
    $ pyauto.sh a.py
    ```

-   `t.sh` run python built in unittest.

    `t.sh` must be run in a module dir such as `humannum`.

    An optional argument can be used to specify what module/class/function to
    test:

    ```
    ./script/t.sh
    ./script/t.sh zkutil
    ./script/t.sh zkutil.test
    ./script/t.sh zkutil.test.test_zkutil
    ./script/t.sh zkutil.test.test_zkutil.TestZKUtil
    ./script/t.sh zkutil.test.test_zkutil.TestZKUtil.test_lock_data
    ```

    One can use `-v` to tell `t.sh` to display verbose info during test:

    -   `t.sh -v` lets python unittest run in verbose mode: to display each
        case function.

    -   `t.sh -vv` or `t.sh -v -v` enables displaying debug message by
        `pykit.ututil.dd()`.

-   `toc.sh` add Table-of-Content to markdown files.

    Usage:

    ```sh
    # build TOC for all *.md
    $ toc.sh

    # build TOC for files:
    $ toc.sh a.md b.md
    ```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
