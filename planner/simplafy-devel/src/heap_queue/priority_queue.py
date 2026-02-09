import heapq
import queue
from typing import Any


class PriorityQueue():
    """My own implementation of a non-thread safe priority queue using heapq
    """

    def __init__(self):
        self._heap = []
        self._index = 0

    def __bool__(self) -> bool:
        return self.is_empty()

    def push(self, item: Any, priority: int):
        heapq.heappush(self._heap, (priority, self._index, item))
        self._index += 1

    def pop(self) -> Any:
        if self._heap:
            return heapq.heappop(self._heap)[-1]
        raise IndexError("pop from an empty priority queue")

    def peek(self) -> Any:
        if self._heap:
            # Return the item with the highest priority without removing it
            return self._heap[0][-1]
        raise IndexError("peek from an empty priority queue")

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def empty(self) -> bool:
        return len(self._heap) == 0

    def size(self) -> int:
        return len(self._heap)

    # Method to comply with the original queue interface
    def get(self, block=False) -> Any:
        if self._heap:
            return heapq.heappop(self._heap)[-1]
        raise IndexError("pop from an empty priority queue")

    def put(self, item: tuple):
        heapq.heappush(self._heap, (item[0], self._index, item))
        self._index += 1
        # self.push(item, item[0])


class ThreadSafePriorityQueue(queue.PriorityQueue):

    def __init__(self):
        super().__init__()
        self._index = 0

    def get(self, block=False) -> Any:
        return super().get()[-1]

    def put(self, item: tuple):
        super().put((item[0], self._index, item))
        self._index += 1
