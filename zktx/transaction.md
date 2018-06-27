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
    - [Solution: re-apply journal and unlock](#solution-re-apply-journal-and-unlock)

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

-   Update `<cluster>/tx/txidset`, mark this journal(tx) has
    been applied and can be removed from `journal` dir safely.

    If there are too many txid in COMMITTED, old txid are moved to PURGED.

    By default it keeps 1024 latest txid in COMMITTED.


## Journal format

A journal contains all record modifications belonging to a single transaction.

The journal node name is the corresponding txid: `00000000001` in
`<cluster>/tx/journal/00000000001`.

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

Value of a record is a json(or yaml) list, which contains one or more `(txid, value)`
pairs(empty list is illegal!).

`txid` is the txid in which a value is applied, value is any json data.

Record format:

```yaml
- [1, {...}]
- [2, {...}]
...
```

> By default a record value keeps the last 16 txid


## Transaction journal and record example

```
/<cluster>/tx/journal/0000000001      # content: {"meta/server/<server_id>": {...}}
/<cluster>/tx/journal/0000000002      # content: {"meta/dirve/<drive_id>": {...}}
/<cluster>/record/meta/server/<server_id>
/<cluster>/record/meta/drive/<drive_id>
```

From above, the journal `0000000001` will be applied to
`/<cluster>/record/meta/server/<server_id>`,
and `0000000002` will be applied to
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
    And the zk-node of a journal is named with txid.

-   keys: records.

    Each record is identified by a key.
    Data of a record is stored in a zk-node.

-   committed-flag: stores tx-id status: COMMITTED or PURGED.

    In our implementation all tx status are stored together in one zk-node:
    `txidset`.

    `txidset` is a dict of 2 `rangeset` for COMMITTED and PURGED:

    ```yaml
    COMMITTED: [[3, 4], [5, 6]]
    PURGED:    [[1, 3]]
    ```

    -   COMMITTED:
        -   If a tx completely committed, its txid is add to `txidset["COMMITTED"]`.
        -   If a tx aborted(for any reason) **AFTER** journal was written, there is a
            chance another tx detected this dead tx and re-do it.
            In this case, eventually the dead tx will be committed, and will be
            added into `txidset["COMMITTED"]`.

    -   PURGED:
        -   If a user explicitly aborts a tx(by calling `tx.abort()`), the txid
            is added into `txidset["PURGED"]`.
        -   If a tx aborted(for any reason) **BEFORE** journal was written,
            another tx will find this dead tx by acquiring a key-lock that the
            dead tx had been held.
            In this case, the other tx will add the dead txid into `txidset["PURGED"]`.
        -   In order to recycle storage space in zk, there is a background
            process cleans up journal. If a journal is removed, its txid is
            added into `txidset["PURGED"]`.

    **PURGED txid set and COMMITTED txid set has no common element**:
    A tx is either COMMITTED or PURGED.

    > It is possible a dead txid not in either of COMMITTED or PURGED, when no
    > one has discovered this tx was dead(another tx will find a dead tx when
    > trying to acquire a key-lock which is held by dead tx, and there is a
    > background process periodically looks up for dead tx).

    A txid that is added into `txidset["PURGED"]` will be removed from
    COMMITTED(to reduce rangeset size).

    Thus all journals those are current available in zk are:
    `txidset["COMMITTED"]`.


# A typical transaction running phases

> Changes: journal-write, record-apply and unlock now are done in a single zk
> request atomically.

```
|     |  action \ resource | tx-lock | 3 key-locks | journal | 3 keys | committed-flag |
| :-- | :--                | :--     | :--         | :--     | :--    | :--            |
| 0   | tx_begin()         | √       |             |         |        |                |
| 1   | lock_get()         | √       | √           |         |        |                |
| 2   | lock_get()         | √       | √√          |         |        |                |
| 3   | lock_get()         | √       | √√√         |         |        |                |
| 4   | commit()           | √       |             | √       | √√√    |                |
|     |    write_journal() |         |             |         |        |                |
|     |    apply()         |         |             |         |        |                |
|     |    unlock_key()    |         |             |         |        |                |
| 5   | add_txidset()      | √       |             | √       | √√√    | √              |
| 6   | unlock_tx()        |         |             | √       | √√√    | √              |
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

## For tx killed in phase 0, 1, 2, 3

Key locks are partially or completely held.

### Condition:

If we found there is **NOT** a journal written, we can be sure that the dead tx
is in phase 0, 1, 2, 3.


### Solution: Abort

Just unlock all seen key locks held by this tx,
because there is no data to commit in journal,
nothing should be applied.

> In these phase there is no way to unlock all keys, because we need to find all
> locked keys in the tx journal, but there is no journal written.
>
> It is possible that a key-lock belonging to a dead tx stays locked for a very
> long time until another tx tries to lock it.

## For tx killed in phase 4, 5, 6

Key locks are all unlocked.
And changes are fully applied to key records.


### Condition:

If we found a journal for this tx


### Solution: re-apply journal and unlock

-   Update the `txidset` for this tx, to mark it as COMMITTED.
