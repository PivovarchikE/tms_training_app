from django.core.cache import caches


class Redis:
    def __init__(self):
        self.cache = caches["redis"]

    def get(self, key):
        print(f"Try to get {key}")
        value = self.cache.get(key)
        print(f"Got {value}")
        return value

    def get_by_pattern(self, pattern):
        print(f"Try to get {pattern}")
        keys = self.cache.keys(f"{pattern}*")
        print(f"Keys: {keys}")
        return keys

    def set(self, key, value, timeout=60 * 20):
        print(f"Try to set {key}")
        self.cache.set(key, value, timeout)

    def delete(self, key):
        print(f"Try to delete {key}")
        self.cache.delete(key)

    def delete_many(self, keys):
        print(f"Try to delete by keys: {keys}")
        self.cache.delete_many(keys)
