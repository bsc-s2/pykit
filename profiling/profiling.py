
import gc
import json
import logging
import os
import sys
import threading
import time

import objgraph
import psutil
import gc
import json
import logging
import os
import sys
import sys
import json
import copy
import Queue

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


def mem_refs():

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


def mem_check2(ii):

    tbl = {}
    ref = {}
    refby = {}

    def add_to_table(obj):

        i = id(obj)

        if i in tbl:
            return

        size = sys.getsizeof(obj, 0)
        cls = _get_class(obj)
        tbl[i] = dict(cls=cls, size=size, obj=obj)

    def add_to_ref(src, dst):

        if src not in ref:
            ref[src] = {}

        ref[src][dst] = True

        if dst not in refby:
            refby[dst] = {}

        refby[dst][src] = True

    for obj in gc.get_objects():

        if not hasattr(obj, '__class__'):
            continue

        add_to_table(obj)
        i = id(obj)

        for sub in gc.get_referents(obj):

            add_to_table(sub)

            subi = id(sub)

            add_to_ref(i, subi)

    # find circle

    reduced = copy.deepcopy(ref)
    circles = []

    while len(reduced) > 0:

        cir = {}
        q = Queue.Queue(1024*1024)
        src = reduced.keys()[0]
        q.put(src)

        while not q.empty():

            src = q.get()

            if src not in reduced:
                continue

            cir[src] = reduced[src]
            del reduced[src]

            for dst in ref[src]:
                if dst not in reduced:
                    continue
                q.put(dst)

            # if src in refby:
            #     for parent in refby[k]:
            #         if parent not in reduced:
            #             continue
            #         q.put(parent)

        circle = {'roots':{}, 'ref': cir}
        circles.append(circle)

        roots = circle['roots']
        for k in cir:
            if k not in refby:
                roots[k] = tbl[k]

        # if ii in cir:
        if len(roots) == 0:
            graph_cycle(circle, tbl)

    # print len(circles)


def make_refby(ref):

    refby = {}

    for src, v in ref.items():
        for dst in v.keys():
            if dst not in refby:
                refby[dst] = {}

            refby[dst][src] = True

    return refby


def find_cycles(ref):

    ref = copy.deepcopy(ref)
    refby = make_refby(ref)

    circles = []

    while len(ref) > 0:

        cir = {}
        q = Queue.Queue(1024*1024)
        k = refby.keys()[0]
        q.put(k)

        while not q.empty():

            k = q.get()

            # k refers to no one
            if k not in ref:
                for i in refby[k]:
                    del ref[i][k]
                    if not ref[i]:
                        del ref[i]

                del refby[k]

            cir[src] = ref[src]
            del ref[src]

            for dst in ref[src]:
                if dst not in ref:
                    continue
                q.put(dst)

            # if src in refby:
            #     for parent in refby[k]:
            #         if parent not in ref:
            #             continue
            #         q.put(parent)

        circle = {'roots':{}, 'ref': cir}
        circles.append(circle)

        roots = circle['roots']
        for k in cir:
            if k not in refby:
                roots[k] = tbl[k]

    return circles


def graph_cycle(circle, tbl):

    cir = remove_leaves(circle['ref'])
    if not cir:
        return

    print '```'
    has = {}
    for v in cir.values():
        for i in v.keys():
            if i not in has:
                print i, tbl[i]['cls'], tbl[i]['size']
                has[i] = True
    print '```'

    print '```graphLR'
    has = {}
    for v in cir.values():
        for i in v.keys():
            if i not in has:
                o = tbl[i]
                rp = o['cls']
                print '{i}("{rp} {i}")'.format(i=i,rp=rp)
                has[i] = True

    for src, refs in cir.items():
        for dst in refs.keys():
            print '{src} --> {dst}'.format(src=src, dst=dst)
    print '```'


def remove_leaves(ref):

    ref = copy.deepcopy(ref)

    running = True
    while running:

        running = False

        for src, v in ref.items():
            for dst in v.keys():
                if dst not in ref:
                    del v[dst]
                    running = True

            if not v:
                del ref[src]

    return ref



def _get_repr(obj):
    return type(obj).__name__


def _get_class(obj):

    if hasattr(obj, '__class__') and hasattr(obj.__class__, '__name__'):
        cls = obj.__class__.__name__
    else:
        cls = str(type(obj))

    return cls



if __name__ == "__main__":

    class One(object):

        def __init__(self, collectible):
            if collectible:
                self.typ = 'collectible'
            else:
                self.typ = 'uncollectible'

                # Make a reference to it self, to form a reference cycle.
                # A reference cycle with __del__, makes it uncollectible.
                self.me = self


        def __del__(self):
            dd('*** __del__ called')

    one = One(False)
    i = id(one)
    del one

    # gc.collect()
    # print gc.garbage
    mem_check2(i)

    sys.exit(0)

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
