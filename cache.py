from collections import OrderedDict
import sys

# todo compress things in the cache

class LRUCache:
    # initialising capacity
    def __init__(self, memory_limit: int):
        self.cache = OrderedDict()
        self.memory_limit_bytes = memory_limit
        self.used_memory = 0

    def get(self, key: str):
        if key not in self.cache:
            return -1
        else:
            # self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: str, value: str):
        if self.used_memory + len(value) < self.memory_limit_bytes:
            self.cache[key] = value
            self.used_memory += len(value)
            # self.cache.move_to_end(key)
            return 0
        else:
            print('reached memory limit')
            return -1
