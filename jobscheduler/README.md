<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Exceptions](#exceptions)
  - [jobscheduler.NextFireTimeError](#jobschedulernextfiretimeerror)
  - [jobscheduler.JobExistError](#jobschedulerjobexisterror)
- [Classes](#classes)
  - [JobScheduler](#jobscheduler)
- [Methods](#methods)
  - [jobscheduler.JobScheduler.schedule](#jobschedulerjobschedulerschedule)
  - [jobscheduler.JobScheduler.add_job](#jobschedulerjobscheduleradd_job)
  - [jobscheduler.JobScheduler.delete_job](#jobschedulerjobschedulerdelete_job)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

jobscheduler

#   Status

The library is considered production ready.

#   Synopsis

```python
from pykit import jobscheduler

def add_number(a, b, c=0):
    print a + b + c

def dump_status(job_status):
    pass

def reload_status():
    pass

def filter_job(job):
    if 'adder' not in job['roles']:
        return False

    return True

jobs = {
    'job_a': {
        'func': add_number,
        'args': [1, 2],
        'kwargs': {'c': 3},
        'every': [1, 'hour'],
        'at': {'minute': 0, 'second': 0},
        'timezone': 'Asia/Shanghai',
        'roles': ['adder']
    },
}

kwargs = {
    'dump_status': dump_status,
    'reload_status': reload_status,
    'filter_job': filter_job,
}

scheduler = jobscheduler.JobScheduler(jobs, **kwargs)
scheduler.schedule()
```

#   Description

This module is used to run jobs at certain time, such as every day at 15:30.

#   Exceptions

## jobscheduler.NextFireTimeError

**syntax**:
`jobscheduler.NextFireTimeError`

Raise if the calculated next fire time is less or equal to the last fire time.
It must be caused by invalid configuration.

## jobscheduler.JobExistError

**syntax**:
`jobscheduler.JobExistError`

Raise if add a job with an already existed job name.

#   Classes

## JobScheduler

**syntax**:
`scheduler = jobscheduler.JobScheduler(jobs, **kwargs)`

**arguments**:

-   `jobs`:
    a dict, key is the name of the job, value is the configuration of the job.
    The configuration is a dict, which contains following fields:

    -   `func`: the function to run, required.

    -   `args`: the args that will be passed to the function, is a list, if do
        not need to pass args, set it to `[]`, do not set it to `None`. Required.

    -   `kwargs`: the keyword arguments that will be passed to the function,
        is a dict, if do not need to pass kwargs, set it to `{}`, do not set it
        to `None`. Required.

    -   `every`: a list with two elements, the first is a number, the
        second is a string to specify unit, which can be one of 'second',
        'minute', 'hour', 'day', 'week' and 'month'. For example,
        `[3, 'hour']` means every 3 hours. Required.

    -   `at`: a dict used to replace corresponding element in the time tuple
        of the next fire time. It may contain following fields: 'second',
        'minute', 'hour', 'day'. Optional.

    -   `timezone`: by default, configurations in `at` use local timezone,
        if you specified configuration in other timezone, you need to set
        `timezone` to the name of that timezone, such as 'Europe/Warsaw' or
        'Asia/Shanghai' and so on. Optional.

    -   `concurrence_n`: set the max number of threads that run the same job
        concurrently. Optional, default is 1.

-   `kwargs`:
    the keyword arguments, following arguments are allowed, none of them
    is mandatory.

    -   `dump_status`: a callback function used to save job status to
        persistent media, so after restart, the status can be reloaded.
        The only argument is the job status, which is a dict.

    -   `reload_status`: a callback function used to reload job status
        from persistent media. No argument.

    -   `filter_job`: a callback function used to check whether a job
        need to run on this machine. Return `True` if need to run, or
        return `False`. The argument is the configuration dict of the job.

#   Methods

## jobscheduler.JobScheduler.schedule

**syntax**:
`scheduler.schedule()`

start to do schedule, it will enter endless loop.

**arguments**
nothing

**return**
not return

## jobscheduler.JobScheduler.add_job

**syntax**:
`scheduler.add_job(job_name, job_conf)`

add a new job.

**arguments**

-   `job_name`: the name of the job.

-   `job_conf`: configuration of the job.

**return**
nothing

## jobscheduler.JobScheduler.delete_job

delete a job.

**syntax**:
`scheduler.delete_job(job_name)`

**arguments**

-   `job_name`: the name of the job.

**return**
nothing

#   Author

Renzhi(任稚) <zhi.ren@baishancloud.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2017 Renzhi(任稚) <zhi.ren@baishancloud.com>
