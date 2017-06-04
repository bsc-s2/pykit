#!/usr/bin/env python2
# coding: utf-8

import ctypes
import inspect
import threading


class AsyncRaiseError(Exception):
    pass


def raise_in_thread(thread, exctype):
    """
    Raises the given exception in the context of the given thread,
    which should cause the thread to exit silently (unless caught).
    """
    if not isinstance(thread, threading.Thread):
        raise TypeError("Only Thread is allowed, got {t}".format(t=thread))

    if thread.is_alive():
        _async_raise(thread.ident, exctype)


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")

    if not issubclass(exctype, BaseException):
        raise ValueError("Only sub classes of BaseException can be raised")

    # PyThreadState_SetAsyncExc requires GIL to be held
    gil_state = ctypes.pythonapi.PyGILState_Ensure()
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid),
                                                     ctypes.py_object(exctype))
    ctypes.pythonapi.PyGILState_Release(gil_state)

    if res == 0:
        raise ValueError("invalid thread id")

    elif res != 1:
        # if it returns a number greater than one, we're in trouble,
        # and we call it again with exc=None to revert the effect.
        gil_state = ctypes.pythonapi.PyGILState_Ensure()
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        ctypes.pythonapi.PyGILState_Release(gil_state)

        raise AsyncRaiseError("PyThreadState_SetAsyncExc failed", res)
