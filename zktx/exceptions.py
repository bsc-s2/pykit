#!/usr/bin/env python
# coding: utf-8

import kazoo.exceptions


class TXError(Exception):
    pass


class Aborted(TXError):
    pass


class NotLocked(Aborted):
    pass


class UnlockNotAllowed(Aborted):
    pass


class RetriableError(TXError):
    pass


class UserAborted(Aborted):
    pass


class HigherTXApplied(Aborted, RetriableError):
    pass


class Deadlock(Aborted, RetriableError):
    pass


class TXTimeout(Aborted):
    pass


class ConnectionLoss(TXError, kazoo.exceptions.ConnectionLoss):
    pass
