# Pykit configuration

`pykit` provides a way to setup config for it.
An end user can config `pykit` behavior without modify source code.


## How it works

Modules those support configuration will load `pykit.config`
and `pykit.config` tries to import `pykitconfig` from `sys.path`.

The `pykit.config` loads attributes defined in `pykitconfig` those it recognizes.


## Usage


### For pykit user

For end user one just creates a file `pykitconfig.py` and adds config into it.
E.g.:

`cat pykitconfig.py`:

```python
import my_project_conf

uid = 2
gid = 3
log_dir = my_project_conf.log_dir
```

And pykit will automatically load `pykitconfig.py` and use them.

```python
from pykit import fsutil
fsutil.write_file('bar', '123') # write_file sets file uid and gid to 2 and 3.
```

### For pykit module developer

-   Add predefined config in `config.py`, to specify the field name default
    value.

    ```python
    # cat pykit/config.py
    uid=_get('uid')
    gid=_get('gid')

    my_conf = _get('my_conf', "default_value")
    ```

-   Import config in you own module

    ```python
    # cat pykit/mymodule/foo.py
    from pykit import config

    print config.my_conf # "default_value"
    ```

##  Supported config

-   `uid`:
    specifies default user-id  when file created, directory made.

-   `gid`:
    specifies default group-id when file created, directory made.

-   `log_dir`:
    specifies default base_dir when logger created.

-   `cat_stat_dir`:
    specifies default stat_dir for all log cat class instances.

-   `iostat_stat_path`:
    specifies the default path to store io stat for `fsutil.iostat`.

-   `zk_node_id`:
    specifies a string to identify this host, by default it is `uuid.getnode()`.

    `ZKLock` uses it to differentiate what host actually holds a lock.

    In `ZKLock`:

    - Different host must specify different `node_id`

    - But A host could specify different `node_id` for different locks.

-   `zk_acl`:
    default acl for new created zk-node.
    Such as `(('xp', '123', 'cdrwa'), ('foo', 'bar', 'rw'))`

-   `zk_auth`:
    default auth info for new connection.
    Such as `('digest', 'xp', '123')`

-   `zk_hosts`:
    default comma separated host list for new connection.
    Such as `'127.0.0.1:2181,128.0.0.8:2181'`

-   `zk_lock_dir`:
    default base dir for `ZKLock` to create lock node.

-   `zk_record_dir`:
    specifies zk node path base dir to store **records** for `zktx`.
    It must ends with `/`.

-   `zk_tx_dir`:
    specifies the base dir of zk node path to store tx related info.
