"""
unittest utility
"""

import inspect
import unittest


def dd(*msg):

    verbosity = get_ut_verbosity()

    if verbosity < 2:
        return

    for m in msg:
        print str(m),
    print


def get_ut_verbosity():
    """
    Return the verbosity setting of the currently running unittest
    program, or 0 if none is running.
    """

    frame = inspect.currentframe()

    while frame:
        self = frame.f_locals.get('self')
        if isinstance(self, unittest.TestProgram):
            return self.verbosity

        frame = frame.f_back

    return 0
