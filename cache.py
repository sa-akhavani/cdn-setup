import zlib


class Cache:
    """
    Implements our cache, which maps wikipedia article names as strings to compressed HTML bodies for those articles

    The cache also manages its own size and ensures that it never stores more data than is specified in its constructor
    """

    # initialising capacity
    def __init__(self, memory_limit):
        self.cache = dict()
        self.memory_limit_bytes = memory_limit  # in bytes
        self.used_memory = 0

    def get(self, key):
        """Returns the decompressed value of the key in the cache, or -1 if it is not in the cache"""
        if key not in self.cache:
            return -1
        else:
            return zlib.decompress(self.cache[key])

    def put(self, key, value, alreadycompressed=False):
        """Compresses the given value and puts it in the cache under the given key if there is room for it,
        returning -1 if there is not room"""

        # handle case where we pre-compress the data for performance
        if alreadycompressed:
            compressed = value
        else:
            compressed = zlib.compress(value)

        # store compressed content if there's room
        if self.used_memory + len(compressed) <= self.memory_limit_bytes:
            self.cache[key] = compressed
            self.used_memory += len(compressed)
            return 0
        else:
            print('reached memory limit')
            return -1
