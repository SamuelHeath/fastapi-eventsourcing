import abc

import redis


class Cache(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def set(self, key: str, value) -> str:
        pass

    @abc.abstractmethod
    def get(self, key: str) -> str:
        pass

    @abc.abstractmethod
    def clear(self, key) -> None:
        pass


class InMemoryCache(Cache):
    def __init__(self):
        self._cache = {}

    def set(self, key, value):
        self._cache[key] = value
        return value

    def get(self, key):
        return self._cache[key]

    def clear(self, key):
        del self._cache[key]


class RedisCache(Cache):
    def __init__(self, cache: redis.Redis):
        self._cache = cache

    def set(self, key, value):
        self._cache.set(key, value)
        return value

    def get(self, key):
        return self._cache.get(key)

    def clear(self, key):
        self._cache.clear(key)
