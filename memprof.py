
def start_mem_check():

    def memory_dump():
        import logging
        try:
            _memory_dump()
        except Exception as e:
            logging.exception(repr(e))

    def _memory_dump():
        import json
        import os
        import sys
        import gc

        with open("/tmp/memory-" + str(os.getpid()), 'w') as f:
            for obj in gc.get_objects():
                i = id(obj)
                size = sys.getsizeof(obj, 0)
                # referrers = [id(o)
                #              for o in gc.get_referrers(obj)
                #              if hasattr(o, '__class__')]
                referents = [id(o)
                             for o in gc.get_referents(obj)
                             if hasattr(o, '__class__')]

                if hasattr(obj, '__class__'):
                    cls = str(obj.__class__)
                    data = {'id': i, 'class': cls, 'size': size, 'referents': referents}
                    f.write(json.dumps(data))
                    # cPickle.dump(data, f)

    def mem_check():

        import os
        import psutil
        import logging

        threshold = 1024 * 1024 * 1024

        while True:
            try:
                rss = psutil.Process(os.getpid()).memory_info().rss

                if rss > threshold:
                    memory_dump()
                    os.abort()
            except Exception as e:
                logging.exception(repr(e))


    import threading
    th = threading.Thread(target=mem_check)
    th.daemon = True
    th.start()

start_mem_check()
