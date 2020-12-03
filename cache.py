import zlib

class Cache:
    # initialising capacity
    def __init__(self, memory_limit):
        self.cache = dict()
        self.memory_limit_bytes = memory_limit
        self.used_memory = 0

    # Compress string before putting them in the cache
    def __compress(self, value):
        compressed = zlib.compress(value.encode())
        return compressed

    # Decompress string before returning to caller
    def __decompress(self, value):
        original = zlib.decompress(value)
        return original.decode()

    # Get value of the key from cache
    def get(self, key):
        if key not in self.cache:
            return -1
        else:
            return self.__decompress(self.cache[key])

    # Put value for the key in cache
    def put(self, key, value):
        compressed = self.__compress(value)
        if self.used_memory + len(compressed) < self.memory_limit_bytes:
            self.cache[key] = compressed
            self.used_memory += len(compressed)
            return 0
        else:
            print('reached memory limit')
            return -1
