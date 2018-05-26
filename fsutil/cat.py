#!/usr/bin/env python2
# coding: utf-8


import errno
import logging
import os
import stat
import time

import __main__
from pykit import config
from pykit import portlock
from pykit import utfjson

from . import fsutil

logger = logging.getLogger(__name__)


no_data_timeout = 3600
read_size = 1024 * 1024 * 16
file_check_time_range = (0.05, 1.0)  # sec
stat_dir = config.cat_stat_dir or '/tmp'
SEEK_START = 'start'
SEEK_END = 'end'


class CatError(Exception):
    pass


class NoData(CatError):
    pass


class NoSuchFile(CatError):
    pass


class LockTimeout(CatError):
    pass


class FakeLock(object):

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        return


class Cat(object):

    def __init__(self, fn,
                 handler=None,
                 file_end_handler=None,
                 exclusive=True,
                 id=None,
                 strip=False,
                 read_chunk_size=read_size):

        self.fn = fn
        self.handler = handler
        self.file_end_handler = file_end_handler
        self.exclusive = exclusive

        if id is None:

            if hasattr(__main__, '__file__'):
                id = __main__.__file__
                id = os.path.basename(id)
                if id == '<stdin>':
                    id = '__stdin__'
            else:
                id = '__instant_command__'

        self.id = id
        self.strip = strip

        read_chunk_size = int(read_chunk_size)
        if read_chunk_size <= 0:
            read_chunk_size = read_size
        self.read_chunk_size = read_chunk_size

        self.running = None
        self.bufferred = None  # (offset, content)

        if (self.handler is not None
                and callable(self.handler)):

            self.handler = [self.handler]

    def cat(self, timeout=None, default_seek=None):

        for line in self.iterate(timeout=timeout, default_seek=default_seek):

            for h in self.handler:
                try:
                    h(line)
                except Exception as e:
                    logger.exception(repr(e)
                                     + ' while handling {line}'.format(line=repr(line)))

    def iterate(self, timeout=None, default_seek=None):
        self.running = True
        try:
            for x in self._iter(timeout, default_seek):
                yield x
        finally:
            self.running = False

    def _iter(self, timeout, default_seek):

        if timeout == 0:
            # timeout at once after one read, if there is no more data in file.
            # set to -1 to prevent possible slight time shift.
            timeout = -1

        if self.exclusive:
            lck = portlock.Portlock(self.lock_name(), timeout=0.1)
        else:
            lck = FakeLock()

        try:
            with lck:
                for x in self._nolock_iter(timeout, default_seek):
                    yield x
        except portlock.PortlockTimeout:
            raise LockTimeout(self.id, self.fn, 'other Cat() has been holding this lock')

    def _nolock_iter(self, timeout, default_seek):

        if timeout is None:
            timeout = no_data_timeout

        expire_at = time.time() + timeout

        while True:

            # NOTE: Opening a file and waiting for new data in it does not work.
            #
            # It has to check for file overriding on fs periodically.
            # Or it may happens that it keeps waiting for new data on a deleted
            # but opened file, while new data is actually written into a new
            # file with the same path.
            #
            # Thus we check if file changed for about 5 times(by reopening it).

            read_timeout = (expire_at - time.time()) / 5.0

            if read_timeout < file_check_time_range[0]:
                read_timeout = file_check_time_range[0]

            if read_timeout > file_check_time_range[1]:
                read_timeout = file_check_time_range[1]

            f = self.wait_open_file(timeout=expire_at - time.time())

            with f:
                try:
                    for x in self.iter_to_file_end(
                            f, read_timeout, default_seek):
                        yield x

                    # re-new expire_at if there is any data read.
                    expire_at = time.time() + timeout
                    if time.time() > expire_at:
                        # caller expect to return at once when it has read once,
                        # timeout < 0

                        # When timeout, it means no more data will be appended.
                        # Thus the bufferred must be a whole line, even there is
                        # not a trailing '\n' presents
                        if self.bufferred is not None:
                            l = self.bufferred[1]
                            self.bufferred = None
                            yield l
                        return

                except NoData as e:

                    # NoData raises only when there is no data yield.

                    logger.info(repr(e) + ' while cat: {fn}'.format(fn=self.fn))

                    if time.time() > expire_at:
                        # raise last NoData
                        raise

    def wait_open_file(self, timeout):

        expire_at = time.time() + timeout
        sleep_time = 0.01
        max_sleep_time = 1

        f = self._try_open_file()
        if f is not None:
            return f

        logger.info('file not found: {fn}'.format(fn=self.fn))

        while time.time() < expire_at:

            f = self._try_open_file()
            if f is not None:
                return f

            sl = min([sleep_time, expire_at - time.time()])
            logger.debug('file not found: {fn}, sleep for {sl}'.format(fn=self.fn, sl=sl))
            time.sleep(sl)

            sleep_time = min([sleep_time * 1.5, max_sleep_time])

        logger.warn('file not found'
                    ' while waiting for it to be present: {fn}'.format(fn=self.fn))

        raise NoSuchFile(self.fn)

    def iter_to_file_end(self, f, read_timeout, default_seek):

        full_chunk_timeout = min([read_timeout * 0.01, 1])

        offset = self.get_last_offset(f, default_seek)
        f.seek(offset)

        logger.info('scan {fn} from offset: {offset}'.format(
            fn=self.fn,
            offset=offset))

        self.wait_for_new_data(f, full_chunk_timeout, read_timeout)
        for line in self.iter_lines(f):
            logger.debug('yield:' + repr(line))
            yield line

        if self.file_end_handler is not None:
            self.file_end_handler()

    def wait_for_new_data(self, f, full_chunk_timeout, timeout):

        # Before full_chunk_expire_at, wait for a full chunk data to be ready to
        # maximize throughput.
        # If time exceeds full_chunk_expire_at, return True if there is any data ready.

        full_chunk_expire_at = time.time() + full_chunk_timeout
        expire_at = time.time() + timeout

        while True:

            if f.tell() + self.read_chunk_size < _file_size(f):
                return

            if (f.tell() < _file_size(f)
                    and time.time() > full_chunk_expire_at):
                return

            if time.time() >= expire_at:
                raise NoData()

            time.sleep(0.05)

    def stat_path(self):
        return os.path.join(stat_dir, self.lock_name())

    def lock_name(self):
        name = os.path.realpath(self.fn)
        name = 'fsutil_cat_lock_!' + self.id + '!'.join(name.split('/'))
        return name

    def read_last_stat(self):

        cont = fsutil.read_file(self.stat_path())
        if cont.startswith('{'):
            return utfjson.load(cont)

        # old format: TODO remove it

        last = cont.strip().split(' ')
        if len(last) != 3:
            raise IOError('InvalidRecordFormat', last)

        (lastino, lastsize, lastoff) = last

        lastino = int(lastino)
        lastoff = int(lastoff)

        return {
            "inode": lastino,
            "offset": lastoff,
        }

    def write_last_stat(self, f, offset):

        st = os.fstat(f.fileno())

        ino = st[stat.ST_INO]

        last = {
            "inode": ino,
            "offset": offset,
        }

        fsutil.write_file(self.stat_path(), utfjson.dump(last))

        logger.info('position written fn=%s inode=%d offset=%d' % (
            self.fn, ino, offset))

    def get_last_offset(self, f, default_seek):
        st = os.fstat(f.fileno())
        ino = st[stat.ST_INO]
        size = st[stat.ST_SIZE]

        max_residual = None

        if default_seek is None or default_seek == SEEK_START:
            default_offset = 0

        elif default_seek == SEEK_END:
            default_offset = size

        elif default_seek < 0:
            max_residual = 0 - default_seek
            default_offset = max(size - max_residual, 0)

        else:
            default_offset = default_seek

        stat_file = self.stat_path()

        if not os.path.isfile(stat_file):
            return default_offset

        try:
            last = self.read_last_stat()
        except (IOError, ValueError):
            # damaged stat file
            return default_offset

        if max_residual is not None:
            if size - last['offset'] > max_residual:
                last['offset'] = size - max_residual

        if last['inode'] != ino or last['offset'] > size:
            return default_offset

        return last['offset']

    def iter_lines(self, f):

        while True:
            offset = f.tell()
            fsize = _file_size(f)
            if offset >= fsize:
                break

            lines = f.readlines(self.read_chunk_size)
            if self.bufferred is not None:
                offset = self.bufferred[0]
                lines[0] = self.bufferred[1] + lines[0]
                self.bufferred = None

            try:
                for l in lines[:-1]:
                    line = l
                    if self.strip:
                        line = line.strip('\r\n')

                    offset += len(l)
                    yield line

                l = lines[-1]
                if not l.endswith(('\r', '\n')):
                    self.bufferred = (offset, l)
                    offset += len(l)
                else:
                    line = l
                    if self.strip:
                        line = line.strip('\r\n')
                    offset += len(l)
                    yield line
            finally:
                self.write_last_stat(f, offset)

    def _try_open_file(self):
        try:
            f = open(self.fn)
            logger.info('file found and opened {fn}'.format(fn=self.fn))
            return f
        except IOError as e:
            if e.errno == errno.ENOENT:
                pass

        return None

    def reset_stat(self):
        stat_path = self.stat_path()
        if not os.path.isfile(stat_path):
            return

        os.remove(stat_path)


def _file_size(f):
    st = os.fstat(f.fileno())
    return st[stat.ST_SIZE]
