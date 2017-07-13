<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Job description](#job-description)
- [Error](#errors)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

wsjobd

#   Status

The library is considered production ready.

#   Synopsis

```python
from collections import OrderedDict
from geventwebsocket import Resource, WebSocketServer
from pykit import wsjobd

def run():
    WebSocketServer(
        ('127.0.0.1', 33445),
        Resource(OrderedDict({'/': wsjobd.JobdWebSocketApplication})),
    ).serve_forever()

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler('wsjobd.log')
    formatter = logging.Formatter('[%(asctime)s, %(levelname)s] %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    run()
```

#   Description

This module based on geventwebsocket, it is the server side of a websocket connection, a client can send a jod description to it, on receiving the job description, it will run that job in a thread, and send progress of the job back to the client periodicly.

#   Job description

Job description is a string formated in json, it is used to tell wsjob what to do, it can contain the following fields:

- `func`
    required. the function of job, it contain module name and function name, seperated by a dot, the module shoud in the `jobs` directory.

- `ident`
    required. the identifier of a job, it is used to prevent from creating the same job repeatedly.

- `progress`
    a dict to set progrss reporting related settings, it can contain the following fields:

    - `interval`
       the interval of progress reporting, default is 5 seconds

    - `key`
        the sub field in which the progress info located

- `check_load`
    a dict to enable system load check, also to set customed thresholds, the can contain the following fields

    - `mem_low_threshold`
        set the min size of available memory the system should have, if not satified, return error. the default is 500M

    - `cpu_low_threshold`
        set the min idle percent of the system cpu, if not satified, return error. the default is 3

    - `max_client_number`
        set the max client number, if this number reached, new connection will be refused. the default is 1000

- `report_system_load`
    a boolean to indicate whether to report system load, if set to true and the progress info is a dict, then the system load info will be add to progress dict by key `system_load`, the value is also a dict, which contains three fields: `mem_available`, `cpu_idle_percent`, `client_number`.

- `cpu_sample_interval`
    set the interval used by psutil.cpu_times_percent, the default is 0.02

#   Errors

if error occur, it will return error code and error message in a json string

##  error code

- SystemOverloadError
- InvalidMessageError
- InvalidProgressError
- LoadingError

#   Author

Renzhi(任稚) <zhi.ren@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Renzhi(任稚) <zhi.ren@baishancloud.com>
