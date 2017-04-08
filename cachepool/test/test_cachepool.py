import unittest

from pykit import ututil
from pykit.cachepool import CachePool
from pykit.cachepool import CachePoolGeneratorError
from pykit.cachepool import make_wrapper

dd = ututil.dd


# Exception that is used for test.
class ErrorInReuse(Exception):
    pass


class StillAllowToReuse(Exception):
    pass


class TestCachePool(unittest.TestCase):

    def test_initial_stat(self):

        pool = CachePool(
            generator,
        )

        dd('pool stat: {0}'.format(pool.stat))

        self.assertEqual(0, pool.stat['new'])
        self.assertEqual(0, pool.stat['put'])
        self.assertEqual(0, pool.stat['get'])

    def test_generator_is_not_callable(self):

        try:
            CachePool(
                1,
            )
        except CachePoolGeneratorError as e:
            self.assertEqual(str(e), 'generator is not callable')

        else:
            self.fail("didn't catch CachePoolGeneratorError")

    def test_generator_run_error_1(self):

        try:
            pool = CachePool(
                lambda x, y: (x, y),
            )
            pool.get()

        except TypeError as e:
            dd(repr(e))

        else:
            self.fail("run generator error")

    def test_generator_run_error_2(self):

        try:
            pool = CachePool(
                lambda x, y: (x, y),
                generator_args=[1, 2],
                generator_argkw={'k': 'v'},
            )
            pool.get()

        except TypeError as e:
            dd(repr(e))

        else:
            self.fail("run generator error")

    def test_generator_run_error_3(self):

        try:
            pool = CachePool(
                lambda x, y: (x, y),
                generator_argkw=[1, 2],
            )
            pool.get()

        except TypeError as e:
            dd(repr(e))

        else:
            self.fail("run generator error")

    def test_close_callback_error(self):

        try:
            pool = CachePool(
                generator,
                close_callback=close_callback_error,
            )
            element = pool.get()
            pool.close(element)

        except AttributeError as e:
            dd(repr(e))

        else:
            self.fail("run close_callback error")

    def test_close_callback(self):

        pool = CachePool(
            generator,
            close_callback=close_callback,
        )
        element = pool.get()

        self.assertFalse(element.closed)
        pool.close(element)
        self.assertTrue(element.closed)

    def test_close_callback_when_queue_full(self):

        pool = CachePool(
            generator,
            pool_size=1,
            close_callback=close_callback,
        )

        dd('pool qsize: {0}'.format(pool.queue.qsize()))
        element1 = pool.get()
        element2 = pool.get()

        pool.put(element1)
        pool.put(element2)

        dd('pool qsize: {0}'.format(pool.queue.qsize()))
        self.assertFalse(element1.closed)
        self.assertTrue(element2.closed)

    def test_pool_size(self):

        pool = CachePool(
            generator,
            pool_size=1,
            close_callback=close_callback,
        )

        element1 = pool.get()
        element2 = pool.get()

        self.assertEqual(0, pool.queue.qsize())
        pool.put(element1)
        self.assertEqual(1, pool.queue.qsize())
        pool.put(element2)
        self.assertEqual(1, pool.queue.qsize())

    def test_get_element(self):

        pool = CachePool(
            generator,
        )

        element = pool.get()

        dd('pool stat: {0}'.format(pool.stat))
        self.assertEqual(1, pool.stat['new'])
        self.assertEqual(1, pool.stat['get'])

        pool.put(element)

        dd('pool stat: {0}'.format(pool.stat))
        self.assertEqual(1, pool.stat['put'])

    def test_get_element_twice(self):

        pool = CachePool(
            generator,
        )

        element1 = pool.get()
        pool.put(element1)

        dd('pool stat: {0}'.format(pool.stat))
        self.assertEqual(1, pool.stat['new'])

        element2 = pool.get()
        pool.put(element2)

        dd('pool stat: {0}'.format(pool.stat))
        self.assertEqual(2, pool.stat['get'])
        self.assertIs(element1, element2)

    def test_args_argkw(self):

        args = [1, 'x']
        argkw = {'key': 'value'}

        pool = CachePool(
            generator,
            generator_args=args,
            generator_argkw=argkw,
        )

        element = pool.get()

        self.assertEqual(element.args[0], args[0])
        self.assertEqual(element.args[1], args[1])
        self.assertEqual(element.argkw, argkw)


class TestWrapper(unittest.TestCase):

    def test_new(self):

        pool = CachePool(
            generator,
        )
        wrapper = make_wrapper(
            pool,
        )

        element1 = element2 = None
        with wrapper() as ele:
            element1 = ele

            with wrapper() as ele:
                element2 = ele

        _element2 = pool.get()
        _element1 = pool.get()

        self.assertIsNot(element1, element2)
        self.assertIs(element1, _element1)
        self.assertIs(element2, _element2)

    def test_reuse(self):

        pool = CachePool(
            generator,
        )
        wrapper = make_wrapper(
            pool,
        )

        element1 = element2 = None
        with wrapper() as ele:
            element1 = ele

        with wrapper() as ele:
            element2 = ele

        _element1 = pool.get()
        _element2 = pool.get()

        self.assertIs(element1, element2)
        self.assertIs(element1, _element1)
        self.assertIs(element2, _element1)
        self.assertIsNot(element2, _element2)

    def test_reuse_decider_error(self):

        pool = CachePool(
            generator,
        )
        wrapper = make_wrapper(
            pool,
            reuse_decider=reuse_decider_error,
        )

        with wrapper() as ele:
            (ele)

        try:
            with wrapper() as ele:
                raise Exception()
        except ErrorInReuse:
            pass

        except:
            self.fail("didn't run reuse_decider")

        else:
            self.fail("didn't run reuse_decider")

    def test_reuse_decider_reuse(self):

        pool = CachePool(
            generator,
            close_callback=close_callback,
        )
        wrapper = make_wrapper(
            pool,
            reuse_decider=reuse_for_acceptable_errors,
        )

        element1 = element2 = None

        try:
            with wrapper() as ele:
                element1 = ele
                raise StillAllowToReuse()
        except:
            pass

        with wrapper() as ele:
            element2 = ele

        self.assertIs(element1, element2)
        self.assertFalse(element1.closed)

    def test_reuse_decider_drop(self):

        pool = CachePool(
            generator,
            close_callback=close_callback,
        )
        wrapper = make_wrapper(
            pool,
            reuse_decider=reuse_for_acceptable_errors,
        )

        element1 = element2 = None

        try:
            with wrapper() as ele:
                element1 = ele
                raise Exception()
        except:
            pass

        with wrapper() as ele:
            element2 = ele

        self.assertIsNot(element1, element2)
        self.assertTrue(element1.closed)
        self.assertFalse(element2.closed)


class Element(object):

    def __init__(self, *args, **argkw):
        self.args = args
        self.argkw = argkw

        self.closed = False

    def close(self):
        self.closed = True

    def do(self):
        print self.args
        print self.argkw


def generator(*args, **argkw):
    return Element(*args, **argkw)


def close_callback(element):
    element.close()


def close_callback_error(element):
    element._close()


def reuse_for_acceptable_errors(errtype, errval, _traceback):
    return errtype in (StillAllowToReuse, )


def reuse_decider_error(errtype, errval, _traceback):
    raise ErrorInReuse()
