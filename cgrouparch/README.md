<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Install](#install)
- [Usage](#usage)
- [Update sub repo](#update-sub-repo)
- [Methods](#methods)
  - [manager.run](#managerrun)
    - [prototype](#prototype)
    - [arguments](#arguments)
  - [get_cgexec_arg](#get_cgexec_arg)
    - [prototype](#prototype-1)
    - [arguments](#arguments-1)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

cgroup_arch:
A python lib used to build cgroup directory tree, add set cgroup pid.

#   Status

This library is in alpha phase.

#   Description

This lib is used to set up cgroup directory tree according to
configuration saved in zookeeper, and add pid to cgroup accordingly.

#   Install

This package does not support installation.

Just clone it and copy it into your project source folder.

```
cd your_project_folder
git clone https://github.com/baishancloud/cgroup_arch.git
```

#   Usage

run manager, the manager will watch on conf in zookeeper,
rebuild cgroup directory tree if conf changed, it also
update cgroup tasks file periodically according to conf.

```python
from cgroup_arch import manager

def get_cgroup_pid_file(cgroup_name):
    if cgroup_name == 'test':
        return ['/tmp/test.pid']
    else:
        return None

def get_zk_host():
    return '127.0.0.1:2181,1.2.3.4:2181'

argkv = {
    'cgroup_dir': '/sys/fs/cgroup',
    'get_cgroup_pid_file': get_cgroup_pid_file,
    'get_zk_host': get_zk_host,
    'zk_prefix': '/cluser_a/service_rank',
    'zk_auth_data': [('digest', 'super:123456')],
    'communicate_ip': '127.0.0.1',
    'communicate_port': '3344',
}

manager.run(**argkv)
```

get cgexec argument, to get the argument('-g cpu:group_foo/sub_group_bar')
used in 'cgexec' tool.

this is usefull if you want to use 'cgexec' tool to run you process in a
cgroup, so the pid of process is added to the cgroup immediately.

you need to provide info about zookeeper, because we need to read the
conf in zookeeper.

```python
from cgroup_arch import manager

argkv = {
    'cgroup_dir': '/sys/fs/cgroup',
    'get_zk_host': get_zk_host,
    'zk_prefix': '/cluser_a/service_rank',
    'zk_auth_data': [('digest', 'super:123456')],
}
cgexec_arg = manager.get_cgexec_arg(['cgroup_foo'], **argkv)

# return like:
# {
#     'cgroup_foo': '-g cpu:group_foo -g blkio:group_bar',
# }
```

#  Update sub repo

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

#   Methods

## manager.run

This function read configuration from etcd and build the cgroup directory
tree accordingly, it alsot  update cgroup pid periodically.

### prototype

```python
run(**argkv)
```

### arguments

It receive the following arguments:

- `get_cgroup_pid_file` is a callback function, the argument to this function is
    the cgroup name, and it should return a list of pid file.

- `get_zk_host` is a callback function, should return etcd hosts, for example:
    '127.0.0.1:2181,1.2.3.4:2181'.

- `zk_prefix` specify the zk key prefix'.

- `zk_auth_data` the zk auth data, for example: `[('digest', 'super:123456')]`.

- `communicate_ip` ip the websocket will listen on.

- `communicate_port` port the websocket will listen on.

- `tasks_update_interval` set cgroup tasks file update interval, in seconds.

- `cgroup_dir` the mount point of the cgroup filesystem,
     default is '/sys/fs/cgroup'.

- `redis_ip` ip of the redis service.

- `redis_ip` port of the redis service.

- `redis_prefix` the key prefix to use when store data into redis.

- `redis_expire_time` we only keep recent data in redis, this
    specify the expire time of data in redis.

- `protected_cgroup` specify a list of cgroup names that you do not
    allow the manager to touch, or the manager will remove all cgroups
    that are not in the conf.

##  get_cgexec_arg

This method used to get the argument used in 'cgexec' tool.

### prototype

```python
manager.get_cgexec_arg(cgroup_names, **argkv)
```

### arguments

It receive the following arguments:

- `cgroup_names` is a list of cgroup_name.

- `argkv` the same as that in `manager.run`, but only `cgroup_dir`,
    `get_zk_host`, `zk_prefix`, `zk_auth_data` are needed.

#   Author

Renzhi (任稚) <zhi.ren@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2016 Renzhi (任稚) <zhi.ren@baishancloud.com>
