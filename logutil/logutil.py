import errno
import logging
import logging.handlers
import os
import sys
import traceback
from stat import ST_DEV
from stat import ST_INO

import __main__
from pykit import config

logger = logging.getLogger(__name__)

log_formats = {
    'default': '[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s',
    'time_level': "[%(asctime)s,%(levelname)s] %(message)s",
    'message': '%(message)s',

    # more info: but it is too long.
    # 'full': '[%(asctime)s,%(process)d-%(thread)d,%(name)s, %(filename)s,%(lineno)d,%(funcName)s %(levelname)s] %(message)s',
}

date_formats = {
    # by default do not specify
    'default': None,
    'time': '%H:%M:%S',
}

log_suffix = 'out'

default_stack_sep = ' --- '


class FixedWatchedFileHandler(logging.FileHandler):
    """
    A handler for logging to a file, which watches the file
    to see if it has changed while in use. This can happen because of
    usage of programs such as newsyslog and logrotate which perform
    log file rotation. This handler, intended for use under Unix,
    watches the file to see if it has changed since the last emit.
    (A file has changed if its device or inode have changed.)
    If it has changed, the old file stream is closed, and the file
    opened to get a new stream.

    This handler is not appropriate for use under Windows, because
    under Windows open files cannot be moved or renamed - logging
    opens the files with exclusive locks - and so there is no need
    for such a handler. Furthermore, ST_INO is not supported under
    Windows; stat always returns zero for this value.

    This handler is based on a suggestion and patch by Chad J.
    Schroeder.
    """

    def __init__(self, filename, mode='a', encoding=None, delay=0):
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)
        self.dev, self.ino = -1, -1
        self._statstream()

    def _statstream(self):
        if self.stream:
            sres = os.fstat(self.stream.fileno())
            self.dev, self.ino = sres[ST_DEV], sres[ST_INO]

    def emit(self, record):
        """
        Emit a record.

        First check if the underlying file has changed, and if it
        has, close the old stream and reopen the file to get the
        current stream.
        """
        # Reduce the chance of race conditions by stat'ing by path only
        # once and then fstat'ing our new fd if we opened a new log stream.
        # See issue #14632: Thanks to John Mulligan for the problem report
        # and patch.
        try:
            # stat the file by path, checking for existence
            sres = os.stat(self.baseFilename)
        except OSError as e:
            if e.errno == errno.ENOENT:
                sres = None
            else:
                raise
        # compare file system stat with that of our stream file handle
        if not sres or sres[ST_DEV] != self.dev or sres[ST_INO] != self.ino:

            # Fixed by xp 2017 Apr 03:
            #     os.fstat still gets OSError(errno=2), although it operates
            #     directly on fd instead of path.  The same for stream.flush().
            #     Thus we keep on trying this close/open/stat loop until no
            #     OSError raises.

            for ii in range(16):
                try:
                    if self.stream is not None:
                        # we have an open file handle, clean it up
                        self.stream.flush()
                        self.stream.close()
                        # See Issue #21742: _open () might fail.
                        self.stream = None
                        # open a new file handle and get new stat info from
                        # that fd
                        self.stream = self._open()
                        self._statstream()
                        break
                except OSError as e:
                    if e.errno == errno.ENOENT:
                        continue
                    else:
                        raise
        logging.FileHandler.emit(self, record)


def get_root_log_fn():

    if hasattr(__main__, '__file__'):
        name = __main__.__file__
        name = os.path.basename(name)
        if name == '<stdin>':
            name = '__stdin__'
        return name.rsplit('.', 1)[0] + '.' + log_suffix
    else:
        return '__instant_command__.' + log_suffix


def make_logger(base_dir=None, log_name=None, log_fn=None,
                level=logging.DEBUG, fmt=None,
                datefmt=None):

    # if log_name is None, get the root logger
    logger = logging.getLogger(log_name)
    logger.setLevel(level)

    if base_dir is None:
        base_dir = config.log_dir

    # do not add 2 handlers to one logger by default
    if len(logger.handlers) == 0:

        if log_fn is None:
            if log_name is None:
                log_fn = get_root_log_fn()
            else:
                log_fn = log_name + '.' + log_suffix

        logger.addHandler(make_file_handler(base_dir, log_fn,
                                            fmt=fmt, datefmt=datefmt))

    return logger


def make_file_handler(base_dir=None, log_fn=None, fmt=None, datefmt=None):

    if base_dir is None:
        base_dir = config.log_dir
    if log_fn is None:
        log_fn = get_root_log_fn()
    file_path = os.path.join(base_dir, log_fn)

    handler = FixedWatchedFileHandler(file_path)
    handler.setFormatter(make_formatter(fmt=fmt, datefmt=datefmt))

    return handler


def set_logger_level(level=logging.INFO, name_prefixes=None):
    if name_prefixes is None:
        name_prefixes = ('',)

    root_logger = logging.getLogger()

    loggers = root_logger.manager.loggerDict.items()
    loggers.sort()

    for name, _ in loggers:
        if name.startswith(name_prefixes):
            name_logger = logging.getLogger(name)
            name_logger.setLevel(level)


def add_std_handler(logger, stream=None, fmt=None, datefmt=None, level=None):

    stream = stream or sys.stdout

    if stream == 'stdout':
        stream = sys.stdout

    elif stream == 'stderr':
        stream = sys.stderr

    stdhandler = logging.StreamHandler(stream)
    stdhandler.setFormatter(make_formatter(fmt=fmt, datefmt=datefmt))
    if level is not None:
        stdhandler.setLevel(level)

    logger.addHandler(stdhandler)

    return logger


def make_formatter(fmt=None, datefmt=None):

    fmt = get_fmt(fmt)
    datefmt = get_datefmt(datefmt)

    return logging.Formatter(fmt=fmt, datefmt=datefmt)


def get_fmt(fmt):

    if fmt is None:
        fmt = 'default'

    return log_formats.get(fmt, fmt)


def get_datefmt(datefmt):

    if datefmt is None:
        return datefmt

    return date_formats.get(datefmt, datefmt)


def stack_list(offset=0):
    offset += 1  # count this function as 1

    # list of ( filename, line-nr, in-what-function, statement )
    x = traceback.extract_stack()
    return x[: -offset]


def stack_format(stacks, fmt=None, sep=None):

    if fmt is None:
        fmt = "{fn}:{ln} in {func} {statement}"

    if sep is None:
        sep = default_stack_sep

    dict_stacks = []
    for st in stacks:
        o = {
            'fn': os.path.basename(st[0]),
            'ln': st[1],
            'func': st[2],
            'statement': st[3],
        }
        dict_stacks.append(o)

    return sep.join([fmt.format(**xx)
                     for xx in dict_stacks])


def stack_str(offset=0, fmt=None, sep=None):
    offset += 1  # count this function as 1
    return stack_format(stack_list(offset), fmt=fmt, sep=sep)


def deprecate(msg=None, fmt=None, sep=None):

    d = 'Deprecated:'

    if msg is not None:
        d += ' ' + str(msg)

    logger.warn(d + (sep or default_stack_sep)
                + stack_str(offset=1, fmt=fmt, sep=sep))
