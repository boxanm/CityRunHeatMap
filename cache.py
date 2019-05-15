import shelve

class Cache:
    """
    Cache based on Python's `shelve` module to keep map tiles.
    WARNING: There is nothing that prevents cache from growing very large
    and also nothing which determines if the data is recent (however the
    time at the moment something is placed in the database is saved).
    """
    def __init__(self, filename):
        """
        Opens an existing shelve and create new one if it does not exist.
        :param filename: Filename for the shelve.
        """
        self.cache = shelve.open(filename, writeback=True)


    def get(self, key):
        """
        Get map tile from cache.
        Null is returned if key does not exist.
        :param key: Key used to retrieve data from the cache.
        """
        try:
            data = self.cache[key][0]
        except:
            data = None
        return data


    def set(self, key, data):
        """
        Stores map tile in cache.
        The data is stored as (tile data, time) tuple.
        :param key: Key used to identify the data.
        :param data: Map tile data.
        """
        if key not in self.cache:
            self.cache[key] = (data, time.time())
        return


    def close(self):
        """
        Close the shelve used to cache the data.
        """
        self.cache.close()
