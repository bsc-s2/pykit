<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Synopsis](#synopsis)
- [Description](#description)
- [Methods](#methods)
  - [jobq.run](#jobqrun)
  - [jobq.stat](#jobqstat)
  - [jobq.EmptyRst](#jobqemptyrst)
  - [jobq.limit_job_speed](#jobqlimitjobspeed)
  - [jobq.JobManager](#jobqjobmanager)
  - [jobq.JobManager.put](#jobqjobmanagerput)
  - [jobq.JobManager.join](#jobqjobmanagerjoin)
  - [jobq.JobManager.set_thread_num](#jobqjobmanagerset_thread_num)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


#   Name

jobq

#   Status

This library is considered production ready.

#   Synopsis

```python
def add1(args):
    return args + 1

def multi2(args):
    return args * 2

def printarg(args):
    print args

jobq.run([0, 1, 2], [add1, printarg])
# > 1
# > 2
# > 3

jobq.run((0, 1, 2), [add1, multi2, printarg])
# > 2
# > 4
# > 6
```

Create 2 threads for job 'multi2':

```python
# As there are 2 thread dealing with multi2, output order will not be kept.
jobq.run(range(3), [add1, (multi2, 2), printarg])
# > 4
# > 2
# > 6
```

Multiple threads with order kept:

```python
# keep_order=True to force to keep order even when with multiple threads.
jobq.run(range(3), [add1, (multi2, 2), printarg],
         keep_order=True)
# > 2
# > 4
# > 6
```

Returning `jobq.EmptyRst` stops passing result to next job:

```python
def drop_even_number( i ):
    if i % 2 == 0:
        return jobq.EmptyRst
    else:
        return i

jobq.run(range(10), [drop_even_number, printarg])
# > 1
# > 3
# > 5
# > 7
# > 9
```

#   Description

Process series of input elements with several functions concurrently and
return once all threads are done.

#   Methods

## jobq.run

**syntax**:
`jobq.run(input, workers, keep_order=False, timeout=None, probe=None)`

Process element from input one by one with functions in workers.

**arguments**:

-   `input`:
    could be an `list`, `tuple`, `dict`, `iterator` or any iterable type that
    can be used in a for-loop.

-   `workers`:
    list of functions, or `tuple` of `(function, nr_of_thread)`,
    or `tuple` of `(function, nr_of_thread, dispatcher_func)`.

    A worker must accept one argument and return one value.
    A typical worker would be defined like:

    ```
    def worker_foo(args):
        result = foo(args)
        return result
    ```

    A worker function can also be an iterator, in which case, jobq
    iterates all elements from returned iterator and pass it to next worker:

    ```
    def worker_iter(args):
        for elt in args:
            yield elt
    ```

    A `dispatcher` is specified by user to control how to dispatch args to
    different workers.
    It should accept one argument `args`, same as the `args` passed to a worker
    function,  and return a `int` indicating which worker to used.

    A dispatcher function might be defined like:

    ```
    def dispatch(args):
        return hash(args) % 5
    ```

    A user-defined dipatcher is used when **concurrency** and **partial-order**
    are both required:
    -   The `args` passed to a same worker is guaranteed to be
        executed in order.
    -   Different workers still run multiple tasks concurrently.

    **If a `dispatcher` specified, it implies `keep_order=True`**.

    Thus a worker group with dispatcher also put result into input queue of next
    worker group with order kept.

-   `keep_order`:
    specifies whether elements must be processed in order.
    Keeping them in order affects performance.

-   `timeout`:
    specifies the max time to run. `None` means to wait until all jobs are
    done.

    If jobq exceeds `timeout` before finishing, it returns and a worker
    quits after it finishs its current job.

-   `probe`:
    a dictionary for stats collecting.
    If it is a valid dictionary, `jobq` writes stats about running jobs to it.
    It can be used with `jobq.stat()` to obtain stat data.

**return**:
None

##  jobq.stat

**syntax**:
`jobq.stat(probe)`

Get stat about a running or finished jobq session.
stat returned format is:

```python
{
    'in': 10,       # number of elements all workers started processing.
    'out': 8,       # number of elements all workers finished processing.
    'doing': 2,     # number of elements all workers is processing.
    'workers': [
        {
            'name': 'example.worker_foo',
            'input': {'size': 3, 'capa': 1024},
            'nr_worker': 2,
            'coordinator': {'size': 3, 'capa': 1024}, # presents only when keep_order=True
        },
        ...
    ]
}
```

**arguments**:
-   `probe`:
    is the dictionary passed into `jobq.run`.

**return**:
stat dictionary.

##  jobq.EmptyRst

**syntax**:
`jobq.EmptyRst`

A worker function return this value to pass nothing to next worker.

```
def worker_back_hole(args):
    return jobq.EmptyRst
```

>   If `None` is returned by a worker, `None` is passed to next worker.

##  jobq.limit_job_speed

**syntax**:
`jobq.limit_job_speed(max_job_speed, job_step)`

A work that limits the speed at which job is executed.

**arguments**:
-   `max_job_speed`:
    is a integer or function, represents the maximum execution job speed,
    If it is a function, use the return value of the function.

-   `job_step`:
    is a integer, represents the step length of a job, the default is 1.

**return**:
None

## jobq.JobManager

**syntax**:
`jobq.JobManager(workers, queue_size=1024, probe=None, keep_order=False)`

It is possible for user to separate worker management and passing in inputs.

```python
def _echo(args):
    print args
    return args

jm = jobq.JobManager([_echo])
for i in range(3):
    jm.put(i)

jm.join()
```

`jobq.JobManager()` create threads for worker functions, and wait for input to
be fed with `jobq.JobManager.put()`.

**arguments**: are the same as `jobq.run`.

## jobq.JobManager.put

**syntax**:
`jobq.JobManager.put(args)`

Put anything as an input element.

**return**:
None

## jobq.JobManager.join

**syntax**:
`jobq.JobManager.join(timeout=None)`

Wait for all worker to finish.

**arguments**:
-   `timeout`:
    is the same as `jobq.run`

**return**:
None


##  jobq.JobManager.set_thread_num

**syntax**:
`jobq.JobManager.set_thread_num(worker, n)`

Change number of threads for a worker on the fly.

If job manager has called `JobManager.join()` to exit,
`set_thread_num` does nothing and just returns silently.

**arguments**:

-   `worker`:
    is the callable passed in when creating JobManager.
    It searches inside job manager for the worker.
    If there is not a worker `is` the one passed in, it raise a
    `JobWorkerNotFound` error.

-   `n`:
    specifies the expected number of threads for this `worker`.

    New threads are created and started before this function returns.
    The threads to remove will be stopped and removed after they finishes
    the job they are currently handling.

**return**:
None


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>




