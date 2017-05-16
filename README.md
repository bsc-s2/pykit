<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
  - [Module List](#module-list)
- [Install](#install)
- [Usage](#usage)
- [Test](#test)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

pykit:
A collection of python libs those are used in project s2: Storage-Service at
baishancloud.com

#   Status

This library is in beta phase.

It has been used heavily in our object storage service, as a foundamental
library of our devops platform.

#   Description

##  Module List

There is a `README.md` for each module.

| name                           | description                                                                           |
| :--                            | :--                                                                                   |
| [cacheable](cacheable)         | Cache data which access frequently                                                    |
| [cachepool](cachepool)         | Reusable object cache in process                                                      |
| [daemonize](daemonize)         | Start, stop or restart a daemon process                                               |
| [dictutil](dictutil)           | Dictionary helper utility                                                             |
| [http](http)                   | HTTP/1.1 client                                                                       |
| [humannum](humannum)           | Convert number to human readable number string                                        |
| [jobq](jobq)                   | Process serial of input elements with several functions concurrently and sequentially |
| [logutil](logutil)             | Unitility functions to create logger or make log message                              |
| [mysqlconnpool](mysqlconnpool) | Mysql connection pool with MySQLdb in python                                          |
| [net](net)                     | Network utility                                                                       |
| [portlock](portlock)           | cross process lock                                                                    |
| [strutil](strutil)             | A collection of helper functions used to manipulate string                            |
| [timeutil](timeutil)           | Support specify time format output and get current ts, ms, us api etc                 |
| [utfjson](utfjson)             | Force `json.dump` and `json.load` in `utf-8` encoding                                 |
| [zkutil](zkutil)               | Unitility functions for zookeeper                                                     |

#   Install

This package does not support installation.

Just clone it and copy it into your project source folder.

```
cd your_project_folder
git clone https://github.com/baishancloud/pykit.git
```

#   Usage

```
from pykit import jobq

def add1(args):
    return args + 1

def printarg(args):
    print args

jobq.run([0, 1, 2], [add1, printarg])
# > 1
# > 2
# > 3
```

#   Test

Run one of following to test all, a module, a TestCase or a function.

```
./script/t.sh
./script/t.sh zkutil
./script/t.sh zkutil.test
./script/t.sh zkutil.test.test_zkutil
./script/t.sh zkutil.test.test_zkutil.TestZKUtil
./script/t.sh zkutil.test.test_zkutil.TestZKUtil.test_lock_data
```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
