import time

from django.core.cache.backends import dummy, locmem
from django.core.cache.backends.base import DEFAULT_TIMEOUT


class DummyCache(dummy.DummyCache):
    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None, nx=None):
        super().set(key, value, timeout, version)
        # mimic the behavior of django_redis with setnx, for tests
        return True


class LocMemCache(locmem.LocMemCache):
    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None, nx=None):
        """
        Optimized in-place replacement for parent set().
        Assumes that timeout logic and `_cache` dict are compatible with Django's LocMemCache.
        Since nx isn't honored (as in the original), we provide set() that always inserts/overwrites.
        """
        if version is None:
            version = self.version
        key = self.make_key(key, version=version)
        if timeout == DEFAULT_TIMEOUT:
            timeout = self.default_timeout
        if timeout is None:
            exp = None
        else:
            exp = time.time() + timeout
        # Direct access to _cache for speed
        self._cache[key] = (exp, value)
        return True
