#!/usr/bin/env python2
# coding: utf-8

import ctypes
import inspect
import threading


class AsyncRaiseError(Exception):
    pass


class InvalidThreadIdError(AsyncRaiseError):
    pass


def start_thread(target, name=None, args=None, kwargs=None, daemon=False):
    args = args or ()
    kwargs = kwargs or {}

    t = threading.Thread(target=target, name=name, args=args, kwargs=kwargs)
    t.daemon = daemon
    t.start()

    return t


def start_daemon_thread(target, name=None, args=None, kwargs=None):
    return start_thread(target, name=name, args=args, kwargs=kwargs,
                        daemon=True)


def raise_in_thread(thread, exctype):
    """
    Asynchronously raises an exception in the context of the given thread,
    which should cause the thread to exit silently (unless caught).

    Raises:
        - InvalidThreadIdError if the given thread is not alive or found.
        - TypeError or ValueError if any input is illegal.
        - AsyncRaiseError for other unexpected errors.
    """
    if not isinstance(thread, threading.Thread):
        raise TypeError("Only Thread is allowed, got {t}".format(t=thread))

    _async_raise(thread.ident, exctype)


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")

    if not issubclass(exctype, BaseException):
        raise ValueError("Only sub classes of BaseException can be raised")

    # PyThreadState_SetAsyncExc requires GIL to be held
    gil_state = ctypes.pythonapi.PyGILState_Ensure()
    try:
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid),
                                                         ctypes.py_object(exctype))
        if res == 0:
            # The thread is likely dead already.
            raise InvalidThreadIdError(tid)

        elif res != 1:
            # If more than one threads are affected (WTF?), we're in trouble, and
            # we try our best to revert the effect, although this may not work.
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)

            raise AsyncRaiseError("PyThreadState_SetAsyncExc failed", res)

    finally:
        ctypes.pythonapi.PyGILState_Release(gil_state)
