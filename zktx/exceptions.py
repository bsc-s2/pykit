#!/usr/bin/env python
# coding: utf-8


class TXError(Exception):
    pass


class TXAborted(TXError):
    pass


class TXUserAborted(TXAborted):
    pass


class TXHigherTXApplied(TXAborted):
    pass


class TXDuplicatedLock(TXAborted):
    pass


class TXTimeout(TXAborted):
    pass


class TXPotentialDeadlock(TXAborted):
    pass


class TXConnectionLost(TXError):
    pass
