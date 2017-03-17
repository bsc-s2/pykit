
import gc
import json
import logging
import os
import sys
import threading
import time

import objgraph
import psutil


def start_mem_check_thread(threshold=1024 * 1024 * 1024,
                           gc=False,
                           size_range=None,
                           interval=1
                           ):
    """
    Start a thread in background and in daemon mode, to watch memory usage.
    If memory this process is using beyond `threshold`, a memory usage profile
    is made and is written to root logger. And process is aborted.

    `threshold`:    maximum memory a process can use before abort.
    `gc`:           whether to run gc every time before checking memory usage.
    `size_range`:   in tuple, dump only object of size in this range.
    `interval`:     memory check interval.
    """

    options = {
        'threshold': threshold,
        'gc': gc,
        'size_range': size_range,
        'interval': interval,
    }

    th = threading.Thread(target=mem_check, args=(options,))
    th.daemon = True
    th.start()

    return th


def mem_check(opts):

    while True:

        if opts['gc']:
            try:
                gc.collect()
            except Exception as e:
                logging.exception(repr(e) + ' while gc.collect()')

        try:
            rss = psutil.Process(os.getpid()).memory_info().rss

            logging.info('current memory used: {rss}'.format(rss=rss))

            if rss > opts['threshold']:
                memory_dump(opts)
                os.abort()
        except Exception as e:
            logging.exception(repr(e) + ' while checking memory usage')

        finally:
            time.sleep(opts['interval'])


def memory_dump(opts):
    try:
        _memory_dump(opts)
    except Exception as e:
        logging.exception(repr(e))


def _memory_dump(opts):

    for typ, n in objgraph.most_common_types():
        logging.info('{typ:30} {n:>10}'.format(typ=typ, n=n))

    objects = []
    rng = opts['size_range']

    summ = {
        'max_refsize': {
            'size': 0,
        },
    }

    for obj in gc.get_objects():

        if not hasattr(obj, '__class__'):
            continue

        size = sys.getsizeof(obj, 0)

        if rng is not None:
            if not (rng[0] <= size < rng[1]):
                continue

        i = id(obj)

        # referrers = [id(o)
        #              for o in gc.get_referrers(obj)
        #              if hasattr(o, '__class__')]

        referents = [(id(o), _get_class(o), sys.getsizeof(o, 0))
                     for o in gc.get_referents(obj)
                     # if hasattr(o, '__class__')
                     ]

        refsize = sum([x[2] for x in referents])

        cls = _get_class(obj)

        data = [
            i,
            cls,
            size,           # object size
            refsize,        # size of all direct referents
            referents,      # referents
        ]

        objects.append(data)

        if summ['max_refsize']['size'] < refsize:

            summ['max_refsize'] = {
                'size': refsize,
                'object': data,
            }

    for o in objects:
        logging.info('memory-dump: ' + json.dumps(o))

    logging.info('memory-dump summary: ' + json.dumps(summ))


def _get_class(obj):

    if hasattr(obj, '__class__') and hasattr(obj.__class__, '__name__'):
        cls = obj.__class__.__name__
    else:
        cls = str(type(obj))

    return cls

if __name__ == "__main__":

    logging.basicConfig(level='DEBUG',
                        format='%(asctime)s,%(name)s,%(levelname)s %(message)s',
                        datefmt='%H:%M:%S'
                        )

    rss = psutil.Process(os.getpid()).memory_info().rss

    logging.info('initial mem:' + repr(rss))

    start_mem_check_thread(threshold=rss + 1024 * 100,
                           interval=0.1)

    a = []

    logging.info('a: ' + str(id(a)))

    while True:
        a.append(str(int(time.time() * 1000)) * 100)
        time.sleep(0.001)
