# A typical transaction running phases

> In this doc `tx` is an abbreviation of `transaction`.

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

-   committed-flag: stores tx-id status: COMMITTED, ABORTED or
    PURGED.

    In our implementation all tx status are stored together in one zk-node:
    `txidset`.

    Its value is 3 set of COMMITTED txid, ABORTED txid and PURGED txid.

```
|     |  action \ resource | tx-lock | 3 key-locks | journal | 3 keys | committed-flag |
| :-- | :--                | :--     | :--         | :--     | :--    | :--            |
| 0   | tx_begin()         | √       |             |         |        |                |
| 1   | lock_get()         | √       | √           |         |        |                |
| 2   | lock_get()         | √       | √√          |         |        |                |
| 3   | lock_get()         | √       | √√√         |         |        |                |
| 4   | write_journal()    | √       | √√√         | √       |        |                |
| 5   | apply(...          | √       | √√√         | √       | √      |                |
| 6   | .....)             | √       | √√√         | √       | √√√    |                |
| 7   | unlock_key(...     | √       |  √√         | √       | √√√    |                |
| 8   | ..........)        | √       |             | √       | √√√    |                |
| 9   | add_txidset()      | √       |             | √       | √√√    | √              |
| a   | unlock_tx()        |         |             | √       | √√√    | √              |
```

A tx may be killed in any step, by any reason.

We have corresponding recovery procedure for each step to guarantee that a tx
either be completely applied or completely aborted.

**Any time a tx runner is killed, tx-lock is deleted automatically(by the
definition of ephemeral node). But key-lock will not be deleted
automatically(key locks are not ephemeral zk node)**.

A redo process first re-acquire the tx-lock, then does the following step:

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

## For tx killed in phase 4, 5, 6, 7, 8, 9

Key locks are all held, and may be partially unlocked.
And changes are partially or fully applied to key records.


### Condition:

If we found a journal for this tx


### Solution: re-apply journal and unlock

-   We apply all changes stored in this journal.

    **Here we must guarantee that re-applying a change has no effect
    on a key record**.

    This is done in the storage layer.

-   Try to release all key locks:

    -   Try to lock it.

    -   If a lock is acquired, just release it.
        **Because a same tx is able to acquire a lock more than one times.**

    -   If a lock is held by others, just skip.

        This means this record has already been unlocked previous and has been locked by other tx.

    This way we release all the key-locks held by a previous dead tx, and leave
    locks held by others intact.

-   Update the `txidset` for this tx, to mark it as COMMITTED.
