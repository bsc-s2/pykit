import logging
import sys
import threading

if sys.version_info > (3,):
    import queue as Queue
else:
    import Queue

logger = logging.getLogger(__name__)


class CachePoolError(Exception):
    pass


class CachePoolGeneratorError(CachePoolError):
    pass


class CachePool(object):

    def __init__(self,
                 generator,
                 generator_args=None,
                 generator_argkw=None,
                 close_callback=None,
                 pool_size=1024):

        self._generator = generator
        self._generator_args = [] if generator_args is None else generator_args
        self._generator_argkw = {} if generator_argkw is None else generator_argkw

        self._close_callback = close_callback

        self._pool_size = pool_size
        self.queue = Queue.Queue(self._pool_size)

        self._stat_lock = threading.RLock()
        self.stat = {
            'new': 0,
            'get': 0,
            'put': 0,
        }

        if not callable(self._generator):
            raise CachePoolGeneratorError('generator is not callable')

    def get(self):

        try:
            element = self.queue.get(block=False)
            with self._stat_lock:
                self.stat['get'] += 1

            logger.debug('reuse: ' + repr(self.stat))
            logger.debug('qzise: ' + repr(self.queue.qsize()))

            return element

        except Queue.Empty:

            element = self._generator(
                *self._generator_args, **self._generator_argkw)

            with self._stat_lock:
                self.stat['new'] += 1
                self.stat['get'] += 1

            logger.debug('new  : ' + repr(self.stat))

            return element

    def put(self, element):

        try:
            self.queue.put(element, block=False)
            with self._stat_lock:
                self.stat['put'] += 1

            logger.debug('put  : ' + repr(self.stat))
            logger.debug('qzise: ' + repr(self.queue.qsize()))

        except Queue.Full:
            self.close(element)

    def close(self, element):

        if ((self._close_callback is not None)
                and callable(self._close_callback)):
            self._close_callback(element)


class CacheWrapper(object):

    def __init__(self, pool, reuse_decider=None):
        self.pool = pool
        self.element = None

        self._reuse_decider = reuse_decider

    def __enter__(self):
        self.element = self.pool.get()
        return self.element

    def __exit__(self, errtype, errval, _traceback):

        if errtype is None:
            self.pool.put(self.element)
        else:
            if ((self._reuse_decider is not None)
                    and callable(self._reuse_decider)
                    and self._reuse_decider(errtype, errval, _traceback)):

                self.pool.put(self.element)

            else:
                self.pool.close(self.element)

        self.element = None


def make_wrapper(pool, reuse_decider=None):

    def _wrapper():
        return CacheWrapper(pool, reuse_decider=reuse_decider)

    return _wrapper
