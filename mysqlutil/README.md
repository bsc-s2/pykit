<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Exceptions](#exceptions)
  - [mysqlutil.ConnectionTypeError](#mysqlutilconnectiontypeerror)
  - [mysqlutil.InvalidLength](#mysqlutilinvalidlength)
- [Methods](#methods)
  - [mysqlutil.gtidset.compare](#mysqlutilgtidsetcompare)
  - [mysqlutil.gtidset.dump](#mysqlutilgtidsetdump)
  - [mysqlutil.gtidset.load](#mysqlutilgtidsetload)
  - [mysqlutil.make_delete_sql](#mysqlutilmake_delete_sql)
  - [mysqlutil.make_index_scan_sql](#mysqlutilmake_index_scan_sql)
  - [mysqlutil.make_insert_sql](#mysqlutilmake_insert_sql)
  - [mysqlutil.make_range_mysqldump_cmd](#mysqlutilmake_range_mysqldump_cmd)
  - [mysqlutil.make_select_sql](#mysqlutilmake_select_sql)
  - [mysqlutil.make_sharding](#mysqlutilmake_sharding)
  - [mysqlutil.make_sql_range_conditions](#mysqlutilmake_sql_range_conditions)
  - [mysqlutil.make_update_sql](#mysqlutilmake_update_sql)
  - [mysqlutil.scan_index](#mysqlutilscan_index)
  - [mysqlutil.query_by_jinja2](#mysqlutilquery_by_jinja2)
  - [mysqlutil.setup_user](#mysqlutilsetup_user)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

#   Name

mysqlutil

#   Status

This library is considered production ready.

#   Description

Mysql related datatype, operations.

#   Exceptions


##  mysqlutil.ConnectionTypeError

**syntax**:
`mysqlutil.ConnectionTypeError`

A subclass of `Exception`, raise if `connpool` in `mysqlutil.scan_index` is not valid.


##  mysqlutil.InvalidLength

**syntax**:
`mysqlutil.InvalidLength`

A subclass of `Exception`, raise when length of list or tuple parameter is not valid.


#   Methods


##  mysqlutil.gtidset.compare

**syntax**:
`mysqlutil.gtidset.compare(a, b)`

Compares two gtidset dictionary and returns the differences.

**arguments**:

-   `a`:
    is a gtidset dictionary, built from `mysqlutil.gtidset.load`.

-   `b`:
    is a gtidset dictionary, built from `mysqlutil.gtidset.load`.

**return**:
a dictionary that describes what gtid is on left side(`a`) only and what gtid is
on right side(`b`) only.

The item `onlyleft` or `onlyright` is a `rangeset.IntIncRangeSet` representing
the gtid range which is on left(right) only, for each uuid.

If there are not any gtid absent on the right side, `onlyleft` is `{"length":0,
"gtidset": {}}` and vice versa:

```
{
    "onlyleft": {
        'length': 45,
        'gtidset': {
            "103a96e9-a030-11e6-b082-a0369fabbda4": [[25, 25]],
            "3f96fb31-6a18-11e6-bd74-a0369fabbdb8": [[1, 30]],
            "630b605d-9ec7-11e6-aae9-a0369fabbdb8": [[1, 4]],
            "83e2adaf-9c37-11e6-9d6e-a0369fb6f7b4": [[61, 70]]
        },
    },
    "onlyright": {
        'length': 81,
        'gtidset': {
            "103a96e9-a030-11e6-b082-a0369fabbda4": [[26, 26]],
            "f4ebb415-a801-11e6-9079-a0369fb4eb00": [[1, 80]]
        },
    },
}
```


##  mysqlutil.gtidset.dump

**syntax**:
`mysqlutil.gtidset.dump(gtidset, line_break='\n')`

Dump gtidset dictionary to string.
See `mysqlutil.gtidset.load`.

**arguments**:

-   `gtidset`:
    is the gtidset dictionary to dump.

-   `line_break`:
    specifies additional separator after "," for each uuid set.
    By default it is `"\n"`.

**return**:
gtidset string.


##  mysqlutil.gtidset.load

**syntax**:
`mysqlutil.gtidset.load(gtidset_str)`

Loads gtidset string and parse it into a dictionary.
The key in the dictionary is the uuid of a mysql instance.
The value is a `rangeset.IntIncRangeSet` instance represents gtid set.

**arguments**:

-   `gtidset_str`:
    is the raw gtidset string read from mysql command, such as
    `Retrieved_Gtid_Set` or `Executed_Gtid_Set` in `show slave status`:

    ```
    Retrieved_Gtid_Set: 9dd98013-a885-11e6-9c9d-a0369fb4eb00:3662619777-3663056053

    Executed_Gtid_Set: 25061445-9f18-11e6-8572-a0369fabbdb8:1-1245974985,
    9dd98013-a885-11e6-9c9d-a0369fb4eb00:1-3663056053,
    dfe3bcd6-6a0f-11e6-82e5-a0369fabbdf0:1-41001
    ```

**return**:
a dictionary in the following format:

```
mysqlutil.gtidset.load(
    '103a96e9-a030-11e6-b082-a0369fabbda4:1-20:25,\n'
    '3f96fb31-6a18-11e6-bd74-a0369fabbdb8:1-30,\n'
    '630b605d-9ec7-11e6-aae9-a0369fabbdb8:1-90,\n'
    '83e2adaf-9c37-11e6-9d6e-a0369fb6f7b4:1-70')

{
    '103a96e9-a030-11e6-b082-a0369fabbda4' : [[1,20], [25, 25]],
    '3f96fb31-6a18-11e6-bd74-a0369fabbdb8' : [[1,30]],
    '630b605d-9ec7-11e6-aae9-a0369fabbdb8' : [[1,90]],
    '83e2adaf-9c37-11e6-9d6e-a0369fb6f7b4' : [[1,70]],
}
```

##  mysqlutil.make_delete_sql

**syntax**:
`mysqlutil.make_delete_sql(table, index, index_values, limit=None)`

Make a sql delete statement.

```
mysqlutil.make_delete_sql('errlog', ('service', 'ip'), ('common0', '127.0.0.1'))
# 'DELETE FROM `errlog` WHERE `service` = "common0" AND `ip` = "127.0.0.1";'

mysqlutil.make_delete_sql('errlog', ('service', 'ip'), ('common0', '127.0.0.1'), limit=1)
# 'DELETE FROM `errlog` WHERE `service` = "common0" AND `ip` = "127.0.0.1" LIMIT 1;'
```

**arguments**:

-   `table`:
    specifies table name from which to delete rows.
    A string or a list or tuple like `(dbname, tablename)`.

-   `index`:
    specifies condition fields to find those rows to delete.
    A list or tuple of strings has the same length with `index_values`.
    If it is `None`, means no `where` condition used in sql delete statement.

-   `index_values`:
    specifies condition values to find those rows to delete.
    A list or tuple has the same length with `index`.

-   `limit`:
    specifies a limited number of rows to delete.
    By default, it is `None`, meams no limit.

**return**:
a string which is a sql delete statement.


## mysqlutil.make_index_scan_sql

**syntax**:
`mysqlutil.make_index_scan_sql(table, result_fields, index, index_values, left_open=False, limit=1024, index_name=None)`

make a sql select statement to scan table with index used.

example:

```
make_index_scan_sql("foo", ['_id', 'key'], ['key', 'val'], ["a", "b"])
# 'SELECT `_id`, `key` FROM `foo` FORCE INDEX (`idx_key_val`) WHERE `key` = "a" AND `val` >= "b" LIMIT 1024'

make_index_scan_sql("foo", ['_id', 'key'], ['key', 'val'], ["a", "b"], index_name="bar")
# 'SELECT `_id`, `key` FROM `foo` FORCE INDEX (`bar`) WHERE `key` = "a" AND `val` >= "b" LIMIT 1024'

make_index_scan_sql("foo", ['_id', 'key'], ['key', 'val'], ["a", "b"], left_open=True)
# 'SELECT `_id`, `key` FROM `foo` FORCE INDEX (`idx_key_val`) WHERE `key` = "a" AND `val` > "b" LIMIT 1024'

make_index_scan_sql(("mydb","foo"), ['_id', 'key'], ['key', 'val'], ["a", "b"], index_name="bar", left_open=True)
# 'SELECT `_id`, `key` FROM `mydb`.`foo` FORCE INDEX (`bar`) WHERE `key` = "a" AND `val` > "b" LIMIT 1024'
```

**arguments**:

-   `table`:
    table name from which to find rows. A string.
    Can also be a list or tuple like `(dbname, tablename)`.

-   `result_fields`:
    column names expected to be returned in result set.
    If it is a blank list or tuple, all columns in the `table` will be returned.
    A list or tuple of strings.

-   `index`:
    specifies condition fields to find rows.
    A list or tuple of strings has the same length with `index_values`.
    If it is `None`, means no `where` condition used in sql select statement.

-   `index_values`:
    specifies condition values to find rows.
    A list or tuple has the same length with `index`.

-   `left_open`:
    if specified and is `True`, the last column in `index` and the corresponding value joined with `>`.
    Otherwise, joined with `>=`.
    By default, it is `False`.

-   `limit`:
    specifies a limited number of rows in the result set to be returned.
    By default, it is 1024.

-   `index_name`:
    specifies an index to use to find rows in the table.
    If it is not `None`, use `index_name` as the force index filed, otherwise `index` is used.
    By default, it is `None`.

**return**:
a string which is a sql select statement.


##  mysqlutil.make_insert_sql

**syntax**:
`mysqlutil.make_insert_sql(table, values, fields=None)`

Make a sql insert statement.

```
mysqlutil.make_insert_sql('errlog', ['common1', '127.0.0.3', '3'])
# 'INSERT INTO `errlog` VALUES ("common1", "127.0.0.3", "3");'

mysqlutil.make_insert_sql(('test', 'errlog'), ['common1', '127.0.0.3', '3'], ['service', 'ip', '_id'])
# 'INSERT INTO `errlog` (`service`, `ip`, `_id`) VALUES ("common1", "127.0.0.3", "3");'
```

**arguments**:

-   `table`:
    specifies table name into which to insert rows.
    A string or a list or tuple like `(dbname, tablename)`.

-   `values`:
    is values to insert into `table`. A list or tuple.

-   `fields`:
    is a subset of fields in `table`, specifies which fields is to insert to.
    A list or tuple of strings.
    If it is specified, should assure that `fields` has the same length with `values`.
    By default, it is `None`.

**return**:
a string which is a sql insert statement.


## mysqlutil.make_range_mysqldump_cmd

**syntax**:
`mysqlutil.make_range_mysqldump_cmd(fields, conn, db, table, path_dump_to, dump_exec, start, end=None)`

Generate mysql dump command for those rows between `start` and `end`: "[`start`, `end`)".

```
make_range_mysqldump_cmd(
    ['bucket_id', 'scope', 'key'],
    {
        'host': '127.0.0.1',
        'user': 'root',
        'passwd': 'password',
        'port': 3306,
    },
    'mysql',
    'key',
    ['/tmp', 'key.sql'],
    ['/user', 'bin', 'mysqldump'],
    ['10', 'a'], ['15', 'd']
)

# "'/usr/bin/mysqldump' --host='127.0.0.1' --port='3306' --user='root' --password='password' 'mysql' 'key' -w "\
# "'(`id` = \"10\" AND `service` >= \"a\") OR (`id` = \"15\" AND `service` < \"d\") OR "\
# "(`id` > \"10\" AND `id` < \"15\")' > '/tmp/key.sql'"
```

**argument**:

-   `fields`:
    is table fields used to find those rows to dump. A list or tuple of string.

-   `conn`:
    is the connection info of the database which dump data from. A dict like:
    ```
    {
        'host': '127.0.0.1',
        'user': 'root',
        'passwd': 'password',
        'port': 3306,
    }
    ```

-   `db`:
    is the database from which dump data. A string.

-   `table`:
    is the name of the table which dump data from. A string.

-   `path_dump_to`:
    is the path which dump data to. A list or tuple of strings, like: `['/tmp', 'table.sql']`. Or a
    string, like `'/tmp/table.sql'`.

-   `dump_exec`:
    is the path where `mysqldump` is. A list or tuple of strings, like:
    `['/usr', 'bin', 'mysqldump']`. Or a string, like `'/usr/bin/mysqldump'`.

-   `start`:
    is the beginning boundary of the condition value, a list or tuple.

-   `end`:
    is the ending boundary of the condition value, a list or tuple. If `end` is `None`,
    then condtion in result has no ending boundary.

**return**:
a string.


##  mysqlutil.make_select_sql

**syntax**:
`mysqlutil.make_select_sql(table, result_fields, index, index_values, limit=None, force_index=None, operator='=')`

Make a sql select statement.

```
make_select_sql('errlog', ['_id', 'key'], ('key', 'val'), ('a', 'b'))
# 'SELECT `_id`, `key` FROM `errlog` WHERE `key` = "a" AND `val` = "b";'

make_select_sql('errlog', ['_id', 'key'], ('key', 'val'), ('a', 'b'),
                limit=1024, force_index="bar", operator='>=')
# 'SELECT `_id`, `key` FROM `errlog` FORCE INDEX (`bar`) WHERE `key` = "a" AND `val` >= "b" LIMIT 1024'
```

**arguments**:

-   `table`:
    table name from which to find rows. A string.
    Can also be a list or tuple like `(dbname, tablename)`.

-   `result_fields`:
    fields expected to be returned in result set.
    If it is `None`, all columns in the `table` will be returned.
    A list or tuple of strings.

-   `index`:
    specifies condition fields to find rows.
    A list or tuple of strings has the same length with `index_values`.
    If it is `None`, means no `where` condition used in sql select statement.

-   `index_values`:
    specifies condition values to find rows.
    A list or tuple has the same length with `index`.

-   `limit`:
    specifies a limited number of rows in the result.
    By default, it is `None`.

-   `force_index`:
    specifies a `force index` statement in result.

-   `operator`:
    specifies condition operator of the last condition in `index`.
    By default, it is '='.

**return**:
a string which is a sql select statement.


## mysqlutil.make_sharding

**syntax**:
`mysqlutil.make_sharding(conf)`

Scan a database table and generate sharding info according configurations in `conf`.
Return sharding result as a dictionary like:
```
{
    "shard": [(), (), ...],
    "number": [number, number, ...],
    "total": number,
}
```

**argument**:

-   `db`: which database to sharding. A string.
-   `table`: which table to sharding. A string.
-   `conn`: database connect info:

    ```
    {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'mysql',
        'passwd': 'password',
    }
    ```

-   `shard_fields`: are index fields to sharding by, a list or tuple of strings.
-   `start`: is the start condition to scan table, a list or tuple of strings.
-   `number_per_shard`: specifies the number of rows a shard contains, an integer.
-   `tolerance_of_shard`: the tolerance of one shard's capacity, an integer.
-   `shard_maker`: a function which accepts one list of strings argument and return a value as
    a "shard" in the result. For example:

    ```
    def shard_maker(shard):
        new_shard = shard + ['']*3
        return new_shard[:3]
    ```
    By default, it is `list`.

**return**:
a dictionary of sharding result, like:
```
{
    "shard": [['10000', 'a', '1'], ['11000', 'b', '3'], ['12000', 'd', '9']],
    "number": [100, 104, 80],
    "total": 284,
}
```

-   `shard`: sharding info, a list of first row of every shard.
-   `number`: numbers of rows of every shard.
-   `total`: number of rows of all shards.


## mysqlutil.make_sql_range_conditions

**syntax**:
`mysqlutil.make_sql_range_conditions(fields, start, end=None)`

Generate sql conditions for those rows in the range of [`start`, `end`).
If `end` is `None`, then no right boundary.

```
make_sql_range_conditions(
    ["bucket_id", "scope", "key"], ("100000000", "a", "key_foo"), ("200000000", "a", "key_bar"))
# ['`bucket_id` = "100000000" AND `scope` = "a" AND `key` >= "key_foo"',
#  '`bucket_id` = "100000000" AND `scope` > "a"',
#  '`bucket_id` > "100000000" AND `bucket_id` < "200000000",
#  '`bucket_id` = "200000000" AND `scope` < "a"',
#  '`bucket_id` = "200000000" AND `scope` = "a" AND `key` < "key_bar"',]
```

**argument**:

-   `fields`:
    is fields to make the conditions. A list or tuple of string.
-   `start`:
    is the beginning boundary of the condition value, a list or tuple of string.
-   `end`:
    is the ending boundary of the condition value, a list or tuple of string.
    If `end` is `None`, then condition in result has no ending boundary.
    By default, it is `None`.

**return**:
a list of string.


##  mysqlutil.make_update_sql

**syntax**:
`mysqlutil.make_update_sql(table, values, index, index_values, limit=None)`

Make a sql update statement.

```
mysqlutil.make_update_sql('errlog', {'_id': '0', 'time': '042718'},
                            ('service', 'ip', '_id'), ('common0', '127.0.0.1', '8'))
# 'UPDATE `errlog` SET `_id` = "0", `time` = "042718" ' \
# 'WHERE `service` = "common0" AND `ip` = "127.0.0.1" AND `_id` = "8";',

mysqlutil.make_update_sql('errlog', {'_id': '0', 'time': '042718'}, None, None, limit=1)
# 'UPDATE `errlog` SET `_id` = "0", `time` = "042718" limit 1'
```

**arguments**:

-   `table`:
    table name from which to update values. A string.
    Can also be a list or tuple like `(dbname, tablename)`.

-   `values`:
    is values to insert into `table`.
    A `dict` whose keys are fields want to update, and values are the update values.

-   `index`:
    specifies condition fields to find those rows to update.
    A list or tuple of strings has the same length with `index_values`.
    If it is `None`, means no `where` condition used in sql update statement.

-   `index_values`:
    specifies condition values to find those rows to update.
    A list or tuple has the same length with `index`.

-   `limit`:
    specifies a limited number of rows in the result.
    By default, it is `None`.

**return**:
a string which is a sql update statement.


## mysqlutil.scan_index

**syntax**:
`mysqlutil.scan_index(connpool, table, result_fields, index_fields, index_values,
                      left_open=False, limit=None, index_name=None, db=None, use_dict=True, retry=0)`

return a generator which generates rows of the sql select result with those arguments once a time.

example:

```
connpool = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'mysql',
    'passwd': '123qwe',
}

rst = scan_index(connpool, 'test-table', ['_id', 'name'], ['foo', 'bar'], ['a', 'b'], db='test-db')

for rr in rst:
    print rr

# {'_id': '1', 'name': 'abb'}
# {'_id': '2', 'name': 'abc'}
# {'_id': '3', 'name': 'abd'}
# ...


connpool = pykit.mysqlconnpool.make(**kwargs)

rst = scan_index(connpool, 'test-table', ['_id'], ['foo', 'bar'], ['a', 'b'], use_dicr=False)

for rr in rst:
    print rr

# ('1', 'abb')
# ('2', 'abc')
# ('3', 'abd')
# ...
```

**argument**:

-   `connpool`:
    provide a connection with a database manager.
    If it is a dict, will be used as an address:

    -   To connect with ip and port, `connpool` is dictionary that contains:

        ```
        {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'mysql',
            'passwd': '123qwe',
        }
        ```

    -   To connect with `unix_socket`, `connpool` is dictionary that contains:

        ```
        {
            'unix_socket': '/tmp/3306.sock',
            'port': 3306,
            'user': 'mysql',
            'passwd': '123qwe',
        }
        ```

    `connpool` can also be a `pykit.mysqlconnpool.MysqlConnectionPool` instance.
    Otherwise, a `ConnectionTypeError` will be raised.

-   `table`:
    table name from which to find rows. A string.
    Can also be a list or tuple like `(dbname, tablename)`.

-   `result_fields`:
    column names expected to be returned in result set.
    If it is a blank list or tuple, all columns in the `table` will be returned.
    A list or tuple of strings.

-   `index_fields`:
    index columns. Use the index consisted of those columns to find rows.
    A list or tuple of strings, has the same length with `index_values`.

-   `index_values`:
    values of the column names in `index_fields`.
    A list or tuple, has the same length with `index_fields`.

-   `left_open`:
    if it is specified and is `True`, the last column in `index_fields` and the corresponding value joined with `>`.
    Otherwise, joined with `>=`.
    By default, it is `False`.

-   `limit`:
    specifies a limited number of rows in the result set to be returned.
    If `limit` is `None`, return all rows in the table.
    By default, it is `None`.

-   `index_name`:
    specifies an index to use to find rows in the table.
    If it is not `None`, use `index_name` as the index and `index_fields` is ignored.

-   `use_dict`:
    if specified and is `False`, return result in list form.
    By default, it is `True`.

-   `retry`:
    try to send query for another N times if connection lost:
    when `MySQLdb.OperationalError` is raised and error code is (2006 or 2013).
    By default, it is 0.

**return**:
a generator which generates rows of the sql select result with those arguments once a time.


##  mysqlutil.query_by_jinja2

**syntax**:
`mysqlutil.query_by_jinja2(conn_argkw, jinja2_argkw)`

Make a `sql` by jinja2 template and send it on the connection.

**arguments**:

-   `conn_argkw`:
    provide a connection with a database manager.

    - If it is a `dict`, see argument `connpool` in `mysql.scan_index`.

    - It can also be a `pykit.mysqlconnpool.MysqlConnectionPool`
      or `MySQLdb.connections.Connection` instance.

-   `jinja2_argkw`:
    a `dict`, the elements:

    -   `template`: the content of the template.

    -   `template_path`: the path of a template file. `template` and `template_path`,
        at least one field must be present.

    -   `vars`: a `dict`, the variables for jinja2 template.

**return**:
query result in a list of dictionary.


##  mysqlutil.setup_user

**syntax**:
`mysqlutil.setup_user(conn_argkw, users)`

Setup users from a MySQL database.

**arguments**:

-   `conn_argkw`:
    see `conn_argkw` in `mysqlutil.query_by_jinja2`.

-   `users`:
    a `list` of `dict`, the element:

    -   `name`: the user name.

    -   `host`: the host for connecting mysql. Defaults to `%`.

    -   `password`: the password of the user.

    -   `priv`: a `str` or a `dict`, the privileges of the users.
        If it is a `str`, the format:`"<db>.<table>:REPLICATION SLAVE,REPLICATION CLIENT"`.
        If it is a `dict`, the key format: `"<db>.<table>"` or `(<db>, <table>)`, the value format:
        `["INSERT", "UPDATE"]`.
        NOTE: **the privilege must be in `mysqlutil.privileges`**

    -   `state`: `present` or `absent`, means grant or revoke the privileges. Defaults to `present`.

**return**:
nothing


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
