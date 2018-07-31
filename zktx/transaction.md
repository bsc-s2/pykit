<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Transaction](#transaction)
  - [Proceeding a transaction](#proceeding-a-transaction)
  - [Journal format](#journal-format)
  - [Record](#record)
  - [Transaction journal and record example](#transaction-journal-and-record-example)
- [Concept](#concept)
- [A typical transaction running phases](#a-typical-transaction-running-phases)
  - [For tx killed in phase 0, 1, 2, 3](#for-tx-killed-in-phase-0-1-2-3)
    - [Condition:](#condition)
    - [Solution: Abort](#solution-abort)
  - [For tx killed in phase 4, 5, 6](#for-tx-killed-in-phase-4-5-6)
    - [Condition:](#condition-1)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Transaction

> In this doc `tx` is an abbreviation of `transaction`.

Transaction is an operation that includes one or many records

> All modifications involved in a transaction should be all committed or be all rollback.

A transaction is protected by a zookeeper lock(a ephemeral node in `<cluster>/lock/*`).
If connection to zookeeper lost, a transaction must stop at once.
Because the locks might be lost.


## Proceeding a transaction

-   Create a transaction id(`txid`, which must be globally unique), by set a zk
    node `<cluster>/tx/txid_maker` and retrieve its latest `version`.

-   Lock this tx, by creating an ephemeral node `<cluster>/tx/alive/<txid>`.

-   Lock and get all records the tx required, such as a region, a block group or
    a server in zookeeper, by creating normal node(**NOT** ephemeral) in
    `<cluster>/lock/*`

    If locking encountered a conflict, wait for the lock holder tx to finish,
    or re-do a dead tx.

    Deadlock detection: if a higher txid found a lower txid holding a lock,
    there is a potential dead lock.
    In this case, the higher txid should release all locks it has held and
    retry.

-   Check if any record has a value with newer txid than this txid,
    to ensure no lower txid will be applied after a higher txid applied.

-   Commit:
    -   Write all modifications into `journal`:
    -   Apply all modifications.
    -   Unlock all locked records.

    These 3 steps are done atomically in a `kazoo.Transaction`.

    > This changed 2018-06.
    > Using a atomic update is much easier to implement.
    > But it does not support cross-zk-cluster tx(E.g. records and journals are in two zk cluster).

-   Update `<cluster>/tx/journal_id_set`, mark this journal has
    been applied and can be removed from `journal` dir safely.

    If there are too many txid in COMMITTED, old txid are moved to PURGED.

    By default it keeps 1024 latest txid in COMMITTED.


## Journal format

A journal contains all record modifications belonging to a single transaction.

We use a sequence node to save journal.

```
# kazootx.create('xx/', '', sequence=True) => xx0000000000
# kazootx.create('xx/a', '', sequence=True) => xx/a0000000000
# so we provide a str "journal_id"
<cluster>/tx/journal/journal_id00000000000
<cluster>/tx/journal/journal_id00000000001
...
```

Data format:

```yaml
"<key>": <value>
"<key>": <value>
```

Where `key` is relative path of a zk node, and `value` is arbitrary json data.


##  Record

A tx would update one or more records.
A record is a zk node in user-defined record base dir, such as
`<cluster>/record/meta/server/<server_id>`.

Record is a `list`, each element is a json(or yaml),
(empty list is illegal!).

Record format:

```
[
    <value1>,
    <value2>,
    ...
]
```

> By default a record keeps the last 16 elements.


## Transaction journal and record example

```
/<cluster>/tx/journal/journal_id0000000000      # content: {"meta/server/<server_id>": {...}}
/<cluster>/tx/journal/journal_id0000000001      # content: {"meta/dirve/<drive_id>": {...}}
/<cluster>/record/meta/server/<server_id>
/<cluster>/record/meta/drive/<drive_id>
```

From above, the journal `journal_id0000000000` will be applied to
`/<cluster>/record/meta/server/<server_id>`,
and `journal_id0000000001` will be applied to
`/<cluster>/record/meta/drive/<drive_id>`,


# Concept


In the following chart it shows how resource status changes when tx action is
taken.

Normally tx resources includes:

-   tx-lock: indicates if a tx is still running. There is only 1 tx-lock for
    each tx.

    It is a ephemeral node in zk.

-   key-locks: for each record involved in a tx there is a corresponding lock
    to protect it.

    Each key-lock is a normal node in zk(not ephemeral).

-   journal: is a zk node that stores all modifications of a tx.

    Journal write is atomic.
    And the zk-node of a journal is created with sequence.

-   keys: records.

    Each record is identified by a key.
    Data of a record is stored in a zk-node.

-   committed-flag: stores journal status: COMMITTED or PURGED.

    In our implementation all journal status are stored together in one zk-node:
    `journal_id_set`.

    `journal_id_set` is a dict of 2 `rangeset` for COMMITTED and PURGED:

    ```yaml
    COMMITTED: [[0, 4]]
    PURGED:    [[0, 1]]
    ```

    -   COMMITTED:
        If a tx completely committed, its journal id is add to `journal_id["COMMITTED"]`.

    -   PURGED:
        If a journal has been deleted, the journal id is add to `journal_id["PURGED"]`


# A typical transaction running phases

> Changes: journal-write, record-apply and unlock now are done in a single zk
> request atomically.

```
|     |  action \ resource      | tx-lock | 3 key-locks | journal | 3 keys | committed-flag |
| :-- | :--                     | :--     | :--         | :--     | :--    | :--            |
| 0   | tx_begin()              | √       |             |         |        |                |
| 1   | lock_get()              | √       | √           |         |        |                |
| 2   | lock_get()              | √       | √√          |         |        |                |
| 3   | lock_get()              | √       | √√√         |         |        |                |
| 4   | commit()                | √       |             | √       | √√√    |                |
|     |    write_journal()      |         |             |         |        |                |
|     |    apply()              |         |             |         |        |                |
|     |    unlock_key()         |         |             |         |        |                |
| 5   | add_to_journal_id_set() |         |             | √       | √√√    | √              |
```

A tx may be killed in any phase, by any reason.

We have corresponding recovery procedure for each phase to guarantee that a tx
either be completely applied or completely aborted.

-   A tx died without finishing phase-4 will be **eventually aborted**.
-   A tx finished phase-4 will be **eventually committed**.

**Any time a tx runner is killed, tx-lock is deleted automatically(by the
definition of ephemeral node). But key-lock will not be deleted
automatically(key locks are not ephemeral zk node)**.

A redo process first re-acquire the tx-lock(in order to ensure no other process
was dealing with this tx), then does the following phase:

## For tx killed in phase 0, 1, 2, 3, 4

Key locks are partially or completely held.

### Condition:

If we found there is **NOT** a journal written, we can be sure that the dead tx
is in phase 0, 1, 2, 3, 4.


### Solution: Abort

Just unlock all seen key locks held by this tx,
because there is no data to commit in journal,
nothing should be applied.

> In these phase there is no way to unlock all keys, because we need to find all
> locked keys in the tx journal, but there is no journal written.
>
> It is possible that a key-lock belonging to a dead tx stays locked for a very
> long time until another tx tries to lock it.

## For tx killed in phase 5

Failed to add journal id to journal id set.

### Condition:

The journal has been written.

### Solution: Wait

When add next journal id to journal id set, the lost journal id will be added too.
