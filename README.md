<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
  - [Module List](#module-list)
- [Install](#install)
- [Usage](#usage)
- [Configuration](#configuration)
  - [Supported config](#supported-config)
- [Test](#test)
- [For developer](#for-developer)
  - [Config](#config)
    - [How it works](#how-it-works)
    - [How to use](#how-to-use)
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
| [argchecker](argchecker)       | Validates arguments against the schema                                                |
| [aws](aws)                     | AWS error codes and so on                                                             |
| [cacheable](cacheable)         | Cache data which access frequently                                                    |
| [cachepool](cachepool)         | Reusable object cache in process                                                      |
| [cluster](cluster)             | Some helper function for the server in a cluster                                      |
| [daemonize](daemonize)         | Start, stop or restart a daemon process                                               |
| [dictutil](dictutil)           | Dictionary helper utility                                                             |
| [etcd](etcd)                   | etcd client                                                                           |
| [fsutil](fsutil)               | File-system Utilities                                                                 |
| [heap](heap)                   | Min heap                                                                              |
| [http](http)                   | HTTP/1.1 client                                                                       |
| [humannum](humannum)           | Convert number to human readable number string                                        |
| [jobq](jobq)                   | Process serial of input elements with several functions concurrently and sequentially |
| [logutil](logutil)             | Utility functions to create logger or make log message                                |
| [mime](mime)                   | Utility functions to handle mime type                                                 |
| [modutil](modutil)             | Submodule Utilities                                                                   |
| [mysqlconnpool](mysqlconnpool) | Mysql connection pool with MySQLdb in python                                          |
| [mysqlutil](mysqlutil)         | Mysql related datatype, operations                                                    |
| [net](net)                     | Network utility                                                                       |
| [portlock](portlock)           | cross process lock                                                                    |
| [priorityqueue](priorityqueue) | Priority queue                                                                        |
| [proc](proc)                   | Utility to create sub process                                                         |
| [rangeset](rangeset)           | Segmented range.                                                                      |
| [ratelimiter](ratelimiter)     | rate limiter                                                                          |
| [redisutil](redisutil)         | For using redis more easily.                                                          |
| [shell](shell)                 | Set different command arguments to execute different functions                        |
| [strutil](strutil)             | A collection of helper functions used to manipulate string                            |
| [threadutil](threadutil)       | Utility functions for better management of threads                                    |
| [timeutil](timeutil)           | Support specify time format output and get current ts, ms, us api etc                 |
| [utfjson](utfjson)             | Force `json.dump` and `json.load` in `utf-8` encoding                                 |
| [utfyaml](utfyaml)             | Force `yaml.dump` and `yaml.load` in `utf-8` encoding                                 |
| [wsjobd](wsjobd)               | Job daemon based on websocket protocol                                                |
| [zkutil](zkutil)               | Utility functions for zookeeper                                                       |


## Module dependency

![](dep-graph.jpg)

#   Install

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


#   Configuration

See [config.md](config.md)


#   Test

Run one of following to test all, a module, a TestCase or a function.

```
./script/t
./script/t zkutil
./script/t zkutil.test
./script/t zkutil.test.test_zkutil
./script/t zkutil.test.test_zkutil.TestZKUtil
./script/t zkutil.test.test_zkutil.TestZKUtil.test_lock_id
```

See [Details](script/README.md)

#   For developer

There are several scripts for developers.
See [script](script).




#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
