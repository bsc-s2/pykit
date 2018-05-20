# A typical transaction running phases

> In this doc `tx` is an abbreviation of `transaction`.

In the following chart it shows how resource status changes when tx action is
taken.

Normally a tx resource includes:

-   tx-lock: indicates if a tx is still running. there is only 1 tx-lock for
    each tx.

-   key-locks: for each record involved in a tx there is a correspoding lock for
    protecting this record.

-   journal: is a storage to store all modifications belonging to a tx.

    Writing into journal is atomic.

-   keys: records storage identified with `key`.

-   committed-flag: a storage that contains tx-id status: COMMITTED, ABORTED or
    PURGED.

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

A tx may be killed in any step.
We have corresponding recovery procedure for each step to guarantee that a tx
either be completely applied or completely aborted.

**Any time a tx runner is killed, tx-lock is lost automatically
but key-lock will not be lost(key locks are permanent)**.

A redo process first re-acquire the tx-lock, then does the following step:

## Phase 0, 1, 2, 3

Key locks are partially or completely held.

### Condition:

If we found there is **NOT** a journal written, we are sure the dead tx is in
phase 0, 1, 2, 3.


### Solution: Abort

Just unlock all seen locked keys,
because there is no data to commit in journal,
nothing will be applied or is already applied.

> In these phase there is no way to unlock all keys, because we need to find all
> locked keys in journal, but there is no journal written.
>
> It is possible a key lock belonging to a dead tx stays locked for a very long
> time until another tx is trying to lock it.

## Phase 4, 5, 6, 7, 8, 9

Key locks are all held.
And changes are partially or fully applied to key records.


### Condition:

If we found a journal for this tx


### Solution: re-apply journal and unlock

-   We apply all changes recorded in this journal.

    **Here we must guarantee that re-applying an earlier changes has no effect
    on a key record**.

    This is done in the storage layer.

-   Try to re-lock all key locks:

    -   If a lock is acquired, just release it.
        **Because a same tx is able to acquire a lock it already held for more
        than one times.**

    -   If a lock is held by others, just ignore.

        This means this key is unlocked and is re-locked by other tx.

    This way we release all the key-locks held by a previous dead tx, and leave
    non-held locks intact.

-   Update the committed-flag for this tx, to mark it as a committed tx.
