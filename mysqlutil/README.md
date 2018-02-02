<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Exceptions](#exceptions)
  - [mysqlutil.ConnectionTypeError](#mysqlutilconnectiontypeerror)
  - [mysqlutil.IndexNotPairs](#mysqlutilindexnotpairs)
- [Methods](#methods)
  - [mysqlutil.gtidset.compare](#mysqlutilgtidsetcompare)
  - [mysqlutil.gtidset.dump](#mysqlutilgtidsetdump)
  - [mysqlutil.gtidset.load](#mysqlutilgtidsetload)
  - [mysqlutil.scan_index](#mysqlutilscan_index)
  - [mysqlutil.sql_condition_between_shards](#mysqlutilsql_condition_between_shards)
  - [mysqlutil.sql_scan_index](#mysqlutilsql_scan_index)
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


##  mysqlutil.IndexNotPairs

**syntax**:
`mysqlutil.IndexNotPairs`

A subclass of `Exception`, raise if length of `index_values` and `index_fields` not equals.


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
    A list or tuple of strings, has the same length with `index_fields`.

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


## mysqlutil.sql_condition_between_shards

**syntax**:
`mysqlutil.sql_condition_between_shards(shard_fields, start, end=None)`

Generate mysql dump conditions for those rows between shard `start` and shard `end`: "[`start`, `end`)".
If `end` is `None`, means that `start` is the last shard.

```
sql_condition_between_shards(
    ["bucket_id", "scope", "key"], ("100000000", "a", "key_foo"), ("200000000", "a", "key_bar"))
# ['`bucket_id` = "100000000" AND `scope` = "a" AND `key` >= "key_foo"',
#  '`bucket_id` = "100000000" AND `scope` > "a"',
#  '`bucket_id` = "200000000" AND `scope` = "a" AND `key` < "key_bar"',
#  '`bucket_id` = "200000000" AND `scope` < "a"',
#  '`bucket_id` > "100000000" AND `bucket_id` < "200000000",]
```

**argument**:

-   `shard_fields`:
    is table fields of which the shard consist. A list or tuple of string.
-   `start`:
    is the beginning boundary of the condition range, a list or tuple of string.
-   `end`:
    is the ending boundary of the condition range, a list or tuple of string. If `end` is `None`,
    then condtion generated has no ending boundary.

**return**:
a list of string.


## mysqlutil.sql_scan_index

**syntax**:
`mysqlutil.sql_scan_index(table, result_fields, index_fields, index_values, left_open=False, limit=1024, index_name=None)`

create a sql select statement with the arguments specified.

example:

```
sql_scan_index("foo", ['_id', 'key'], ['key', 'val'], ["a", "b"])
# 'SELECT `_id`, `key` FROM `foo` FORCE INDEX (`idx_key_val`) WHERE `foo`.`key` = "a" AND `foo`.`val` >= "b" LIMIT 1024'

sql_scan_index("foo", ['_id', 'key'], ['key', 'val'], ["a", "b"], index_name="bar")
# 'SELECT `_id`, `key` FROM `foo` FORCE INDEX (`bar`) WHERE `foo`.`key` >= "a"  LIMIT 1024'

sql_scan_index("foo", ['_id', 'key'], ['key', 'val'], ["a", "b"], left_open=True)
# 'SELECT `_id`, `key` FROM `foo` FORCE INDEX (`idx_key_val`) WHERE `foo`.`key` > "a"  LIMIT 1024'

sql_scan_index(("mydb","foo"), ['_id', 'key'], ['key', 'val'], ["a", "b"], index_name="bar", left_open=True)
# 'SELECT `_id`, `key` FROM `mydb`.`foo` FORCE INDEX (`bar`) WHERE `mydb`.`foo`.`key` > "a"  LIMIT 1024'
```


**arguments**:

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
    A list or tuple of strings, has the same length with `index_fields`.

-   `left_open`:
    if specified and is `True`, the last column in `index_fields` and the corresponding value joined with `>`.
    Otherwise, joined with `>=`.
    By default, it is `False`.

-   `limit`:
    specifies a limited number of rows in the result set to be returned.
    By default, it is 1024.

-   `index_name`:
    specifies an index to use to find rows in the table.
    If it is not `None`, use `index_name` as the index and `index_fields` is ignored.

**return**:
a string which is a sql select statement.


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
