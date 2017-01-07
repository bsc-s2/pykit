<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
  - [Module List](#module-list)
- [Install](#install)
- [Usage](#usage)
  - [Update sub repo](#update-sub-repo)
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

There are several native modules like `utfjson`,
along with several external modules like `jobq`, which are imported with
`script/git-subrepo`(`git-subrepo` is also maintained by itself).

##  Module List

There is a `README.md` for each module.

| name                           | description                                                                           |
| :--                            | :--                                                                                   |
| script/git-subrepo             | A shell script maintaining sub module                                                 |
| [cachepool](cachepool)         | Reusable object cache in process                                                      |
| [daemonize](daemonize)         | Start, stop or restart a daemon process                                               |
| [dictutil](dictutil)           | Dictionary helper utility                                                             |
| [humannum](humannum)           | Convert number to human readable number string                                        |
| [jobq](jobq)                   | Process serial of input elements with several functions concurrently and sequentially |
| [mysqlconnpool](mysqlconnpool) | Mysql connection pool with MySQLdb in python                                          |
| [net](net)                     | Network utility                                                                       |
| [strutil](strutil)             | A collection of helper functions used to manipulate string                            |
| [utfjson](utfjson)             | Force `json.dump` and `json.load` in `utf-8` encoding                                 |
| [timeutil](timeutil)           | Support specify time format output and get current ts, ms, us api etc                 |
| [portlock](portlock)           | cross process lock                                                                    |

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

##  Update sub repo

>   You do not need to read this chapter if you are not a maintainer.

First update sub repo config file `.gitsubrepo`
and run `git-subrepo`.

`git-subrepo` will fetch new changes from all sub repos and merge them into
current branch `mater`:

```
./script/git-subrepo/git-subrepo
```

`git-subrepo` is a tool in shell script.
It merges sub git repo into the parent git working dir with `git-submerge`.

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
