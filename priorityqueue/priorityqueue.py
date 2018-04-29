import Queue
import threading

from pykit import heap

default_priority = 10.0

Empty = Queue.Empty


class Producer(object):

    def __init__(self, producer_id, priority, iterable):
        self.consumed = 0
        self.iterable_lock = threading.RLock()
        self.stat = {'get': 0}
        self.cmp_key = (0, 0)

        self.producer_id = producer_id
        self.set_priority(priority)
        self.set_iterable(iterable)

    def get(self):

        with self.iterable_lock:
            try:
                val = self.iterable.next()
                self.stat['get'] += 1
                self.consume()
                return val
            except StopIteration:
                raise Empty('no more item in ' + str(self))

    def set_priority(self, priority):

        priority = float(priority)

        if priority <= 0:
            raise ValueError('priority can not be less or euqal 0: ' + str(priority))

        self.priority = priority
        self.item_cost = default_priority / float(self.priority)
        self.cmp_key = (self.consumed, self.item_cost)

    def set_iterable(self, iterable):
        self.iterable = iter(iterable)

    def consume(self):
        self.consumed += self.item_cost
        self.cmp_key = (self.consumed, self.item_cost)

    def __str__(self):
        return '[{producer_id}={priority} c={consumed}]'.format(
            producer_id=self.producer_id,
            priority=self.priority,
            consumed=self.consumed,
        )

    def __lt__(self, b):
        return self.cmp_key < b.cmp_key


class PriorityQueue(object):

    def __init__(self):
        self.producer_by_id = {}

        # empty_heap: stores all empty Producer.
        #             Empty produer means it has raised an Empty exception when
        #             calling Producer.get().
        #             `Empty` exception raised means it has no more item to
        #             produce.
        #
        # consumable_heap: stores all non-empty Producer, less consumed
        #             Producer is at high position in heap.
        self.empty_heap = heap.RefHeap()
        self.consumable_heap = heap.RefHeap()

        self.heap_lock = threading.RLock()

    def add_producer(self, producer_id, priority, iterable):

        with self.heap_lock:
            if producer_id not in self.producer_by_id:
                p = Producer(producer_id, priority, iterable)
                self.producer_by_id[producer_id] = p
            else:
                # if exist, update its priority and iterable.
                p = self.producer_by_id[producer_id]
                p.set_priority(priority)
                p.set_iterable(iterable)

            # Every time add a (may be existent) queue, treat it as consumable
            self._remove_from_heaps(p)
            self.consumable_heap.push(p)

    def remove_producer(self, producer_id, ignore_not_found=False):

        with self.heap_lock:
            if producer_id not in self.producer_by_id and ignore_not_found:
                return

            p = self.producer_by_id[producer_id]
            self._remove_from_heaps(p)

            del self.producer_by_id[producer_id]

    def _remove_from_heaps(self, producer):

        try:
            self.empty_heap.remove(producer)
        except heap.NotFound:
            pass

        try:
            self.consumable_heap.remove(producer)
        except heap.NotFound:
            pass

    def get(self):

        while True:

            with self.heap_lock:
                try:
                    p = self.consumable_heap.get()
                except heap.Empty:
                    raise Empty('no more queue has any item')

                try:
                    # NOTE: if p.iterable blocks, everything is blocked
                    val = p.get()

                except Empty:

                    self.consumable_heap.remove(p)
                    self.empty_heap.push(p)

                    # try next consumable queue
                    continue

                self.consumable_heap.sift(p)

                return val

    def __str__(self):
        qs = []
        for cq in self.producer_by_id.values():
            qs.append(str(cq))

        return ' '.join(qs)
