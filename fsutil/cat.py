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
stat_dir = config.cat_stat_dir or '/tmp'


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
                 strip=False):

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
        self.running = None

        if (self.handler is not None
                and callable(self.handler)):

            self.handler = [self.handler]

    def cat(self, timeout=None):

        for line in self.iterate(timeout=timeout):

            for h in self.handler:
                try:
                    h(line)
                except Exception as e:
                    logger.exception(repr(e)
                                     + ' while handling {line}'.foramt(line=repr(line)))

    def iterate(self, timeout=None):
        self.running = True
        try:
            for x in self._iter(timeout=timeout):
                yield x
        finally:
            self.running = False

    def _iter(self, timeout):

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
                for x in self._nolock_iter(timeout=timeout):
                    yield x
        except portlock.PortlockTimeout:
            raise LockTimeout(self.id, self.fn, 'other Cat() has been holding this lock')

    def _nolock_iter(self, timeout=None):

        if timeout is None:
            timeout = no_data_timeout

        expire_at = time.time() + timeout

        while True:

            f = self.wait_open_file(timeout=expire_at - time.time())

            with f:
                try:
                    for x in self.iter_to_file_end(f, read_timeout=expire_at - time.time()):
                        yield x

                    # re-new expire_at if there is any data read.
                    expire_at = time.time() + timeout
                    if time.time() > expire_at:
                        # caller expect to return at once when it has read once,
                        # timeout < 0
                        return

                except NoData as e:

                    # NoData raises only when there is no data yield.

                    logger.info(repr(e) + ' while cat: {fn}'.format(fn=self.fn))

                    if time.time() > expire_at:
                        # raise last NoSuchFile or NoData
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

    def iter_to_file_end(self, f, read_timeout):

        full_chunk_timeout = min([read_timeout * 0.01, 1])

        offset = self.get_last_offset(f)
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

            if f.tell() + read_size < _file_size(f):
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

    def get_last_offset(self, f):

        st = os.fstat(f.fileno())
        ino = st[stat.ST_INO]
        size = st[stat.ST_SIZE]

        try:
            last = self.read_last_stat()
        except IOError:
            # no such file
            last = {'inode': 0, 'offset': 0}

        if last['inode'] == ino and last['offset'] <= size:
            return last['offset']
        else:
            return 0

    def iter_lines(self, f):

        while True:
            offset = f.tell()
            if offset >= _file_size(f):
                break

            lines = f.readlines(read_size)

            try:
                for l in lines:
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


def _file_size(f):
    st = os.fstat(f.fileno())
    return st[stat.ST_SIZE]
