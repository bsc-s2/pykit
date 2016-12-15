#!/usr/bin/env python

import jobq

if __name__ == "__main__":

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

    # Specify number of threads for each job:

    # Job 'multi2' uses 1 thread.
    # This is the same as the above example.
    jobq.run(range(3), [add1, (multi2, 1), printarg])
    # > 2
    # > 4
    # > 6

    # Create 2 threads for job 'multi2':

    # As there are 2 thread dealing with multi2, output order will not be kept.
    jobq.run(range(3), [add1, (multi2, 2), printarg])
    # Output could be:
    # > 4
    # > 2
    # > 6

    # Multiple threads with order kept:

    # keep_order=True to force to keep order even with concurrently running.
    jobq.run(range(3), [add1, (multi2, 2), printarg],
             keep_order=True)
    # > 2
    # > 4
    # > 6

    # timeout=0.5 specifies that it runs at most 0.5 second.
    jobq.run(range(3), [add1, (multi2, 2), printarg],
             timeout=0.5)

    # Returning *jobq.EmptyRst* stops delivering result to next job:

    def drop_even_number(i):
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
