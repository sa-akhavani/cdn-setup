from collections import OrderedDict
import sys

class LRUCache:
    # initialising capacity
    def __init__(self, memory_limit: int):
        self.cache = OrderedDict()
        self.memory_limit_bytes = memory_limit

    def get(self, key: str):
        if key not in self.cache:
            return -1
        else:
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: str, value: str):
        self.cache[key] = value
        self.cache.move_to_end(key)
        
        # process_current_memory_usage = sys.getsizeof(self.cache)
        # if process_current_memory_usage > self.memory_limit_bytes:
        #     self.cache.popitem(last = False)