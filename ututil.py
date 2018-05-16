"""
unittest utility
"""

import inspect
import logging
import os
import time
import unittest

_glb = {
    'unittest_logger': None,
}

debug_to_stdout = os.environ.get('UT_DEBUG') == '1'


# TODO make this configurable
# logging.basicConfig(level='INFO',
#                     format='[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s',
#                     datefmt='%H:%M:%S'
#                     )

# logger = logging.getLogger('kazoo')
# logger.setLevel('INFO')


class Timer(object):

    def __init__(self):
        self.start = None
        self.end = None

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, errtype, errval, _traceback):
        self.end = time.time()

    def spent(self):
        return (self.end or time.time()) - self.start


class ContextFilter(logging.Filter):

    """
    Add correct func, line number, line info to log record.

    To fix the issue that when test case function use dd() instead of
    logger.debug(), logging alwasy print context info of dd(), but not the
    caller test_xxx.
    """

    def filter(self, record):

        # skip this function
        stack = inspect.stack()[1:]

        for i, (frame, path, ln, func, line, xx) in enumerate(stack):

            if (frame.f_globals.get('__name__') == 'pykit.ututil'
                    and func == 'dd'):

                # this frame is dd(), find the caller
                _, path, ln, func, line, xx = stack[i + 1]

                record._fn = os.path.basename(path)
                record._ln = ln
                record._func = func
                return True

        record._fn = record.filename
        record._ln = record.lineno
        record._func = record.funcName
        return True


def _init():

    if _glb['unittest_logger'] is not None:
        return

    # test_logutil might require this module and logutil is still under test!
    try:
        from pykit import logutil
        logger = logutil.make_logger(
            '/tmp',
            log_name='unittest',
            level='DEBUG',
            fmt=('[%(asctime)s'
                 ' %(_fn)s:%(_ln)d'
                 ' %(levelname)s]'
                 ' %(message)s'
                 )
        )
        logger.addFilter(ContextFilter())

        _glb['unittest_logger'] = logger

    except Exception as e:
        print repr(e) + ' while init root logger'


def dd(*msg):
    """
    debug level logging in a test case function test_xx.

    dd() write log to stdout if unittest verbosity is 2.
    And dd always write log to log file in /tmp dir.
    """

    s = ' '.join([x.encode('utf-8') if isinstance(x, unicode) else str(x)
                    for x in msg])

    _init()

    l = _glb['unittest_logger']
    if l:
        l.debug(s)

    if not debug_to_stdout:
        return

    print s


def get_ut_verbosity():
    """
    Return the verbosity setting of the currently running unittest
    program, or 0 if none is running.
    """

    frame = _find_frame_by_self(unittest.TestProgram)
    if frame is None:
        return 0

    self = frame.f_locals.get('self')

    return self.verbosity


def get_case_logger():
    """
    Get a case specific logger.
    The logger name is: `<module>.<class>.<function>`,
    such as: `pykit.strutil.test.test_strutil.TestStrutil.test_format_line`

    It must be called inside a test_* function of unittest.TestCase, or no
    correct module/class/function name can be found.
    """

    frame = _find_frame_by_self(unittest.TestCase)

    self = frame.f_locals.get('self')

    module_name = frame.f_globals.get('__name__')
    class_name = self.__class__.__name__
    func_name = frame.f_code.co_name

    nm = module_name + '.' + class_name + '.' + func_name

    logger = logging.getLogger(nm)
    for f in logger.filters:
        if isinstance(f, ContextFilter):
            break
    else:
        logger.addFilter(ContextFilter())

    return logger


def _find_frame_by_self(clz):
    """
    Find the first frame on stack in which there is local variable 'self' of
    type clz.
    """

    frame = inspect.currentframe()

    while frame:
        self = frame.f_locals.get('self')
        if isinstance(self, clz):
            return frame

        frame = frame.f_back

    return None
