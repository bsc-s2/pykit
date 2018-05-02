<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Synopsis](#synopsis)
- [Methods](#methods)
  - [manager.run](#managerrun)
  - [get_cgexec_arg](#get_cgexec_arg)
- [Read cgroup usage info data](#read-cgroup-usage-info-data)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

cgrouparch

A python lib used to build cgroup directory tree, add set cgroup pid.

#   Status

This library is considered production ready.

#   Description

This lib is used to set up cgroup directory tree according to
configuration saved in zookeeper, and add pid to cgroup accordingly.


#   Synopsis

Start the manager, the manager will watch on conf in zookeeper,
rebuild cgroup directory tree if conf changed, it also
update cgroup tasks file periodically according to conf.

```python
# configuration in zookeeper:
{
    'cpu': {
        'sub_cgroup': {
            'test_cgroup_a': {
                'conf': {
                    'share': 1024,
                },
            },
            'test_cgroup_b': {
                'conf': {
                    'share': 100,
                },
                'sub_cgroup': {
                    'test_cgroup_b_sub1': {
                        'conf': {
                            'share': 200,
                        },
                    },
                },
            },
        },
    },
}

from pykit.cgrouparch import manager

def get_cgroup_pid_file(cgroup_name):
    if cgroup_name == 'test_cgroup_a':
        return ['/tmp/test.pid']
    # ...

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

Get `cgexec` argument, to get the argument(for example:
'-g cpu:test_cgroup_b/test_cgroup_b_sub1') used in `cgexec` command.

This is usefull if you want to use `cgexec` command to run you process in a
cgroup, so the pid of process is added to the cgroup immediately.

You need to provide info about zookeeper, because we need to read the
conf in zookeeper.

```python
from pykit.cgrouparch import manager

argkv = {
    'cgroup_dir': '/sys/fs/cgroup',
    'get_zk_host': get_zk_host,
    'zk_prefix': '/cluser_a/service_rank',
    'zk_auth_data': [('digest', 'super:123456')],
}
cgexec_arg = manager.get_cgexec_arg(['test_cgroup_a'], **argkv)

# return like:
# {
#     'test_cgroup_a': '-g cpu:test_cgroup_a',
# }
```

#   Methods

## manager.run

**syntax**:
`manager.run(**argkv)`

This function read configuration from zookeeper and build the cgroup
directory tree accordingly, it also  update cgroup pid periodically.
Every second it save usage info of each cgroup in redis, you can read
usage info through websocket protocol.

**arguments**:

-   `get_cgroup_pid_file`:
    a callback function, the argument is the cgroup name, and it
    should return a list of pid files. Required.

-   `get_zk_host`:
    a callback function, should return zookeeper hosts, for example:
    '127.0.0.1:2181,1.2.3.4:2181'. Required.

-   `zk_prefix`:
    specify the zookeeper key prefix'. Required.

-   `zk_auth_data`:
    specify zookeeper auth data, for example: `[('digest', 'super:123456')]`.
    Required.

-   `communicate_ip`:
    specify ip address the websocket server will bind. Default to '0.0.0.0'.

-   `communicate_port`:
    specify port the websocket server will bind. Default to 43409.

-   `tasks_update_interval`:
    set cgroup tasks file update interval in seconds. Default to 30.

-   `cgroup_dir`:
    the mount point of the cgroup filesystem, default to '/sys/fs/cgroup'.

-   `redis_ip`:
    ip of the redis server. Required.

-   `redis_port`:
    port of the redis server. Required.

-   `redis_prefix`:
    the key prefix to use when saving usage info into redis.

-   `redis_expire_time`:
    we only keep recent usage info in redis, this specify the
    expire time in seconds of usage info data in redis.  Default to 300.

-   `protected_cgroup`:
    specify a list of cgroup names that you do not allow the manager
    to touch, or the manager will remove all cgroups that are not
    in the conf. Optional.

**return**
Not return

##  get_cgexec_arg

**syntax**:
`manager.get_cgexec_arg(cgroup_names, **argkv)`

This method used to get the argument used in `cgexec` command.

**arguments**:

-   `cgroup_names`:
    a list of cgroup names.

-   `argkv`:
    the same as that in `manager.run`, but only `cgroup_dir`,
    `get_zk_host`, `zk_prefix`, `zk_auth_data` are needed.

**return**

A dict contains argument for `cgexec` of each input cgroup.

#   Read cgroup usage info data

You can read usage data of each cgroup of each second through
websocket protocol.

``` python
import json
import websocket

body = {
    'cmd': 'show_account',
    'args': {
        'nr_slot': 2,
    },
}

ws = websocket.WebSocket()
ws.connect('ws://127.0.0.1:43409')
ws.send(json.dumps(body))
print ws.recv()

# output example:
{
    "1525258774": {
        "cpu": {
            "value": {
                "usage": 1446489231295
            },
            "sub_cgroup": {
                "test_cgroup_a": {
                    "value": {
                        "usage": 192790540163
                    },
                },
                "test_cgroup_b": {
                    "value": {
                        "usage": 192790540163
                    },
                    "sub_cgroup": {
                        "test_cgroup_b_sub1": {
                            "value": {
                                "usage": 3928774282
                            },
                        },
                    },
                },
            },
        },
        "blkio": {
            ...
        },
    },
    "1525258775": {
        ...
    }
}
```

#   Author

Renzhi (任稚) <zhi.ren@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2016 Renzhi (任稚) <zhi.ren@baishancloud.com>
