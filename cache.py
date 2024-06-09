import functools
import time
import threading
import logging
from typing import List, Any, Tuple

def make_hashable(item):
    if isinstance(item, list):
        return tuple(item)
    elif isinstance(item, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in item.items()))
    return item

def time_limited_cache(max_age_seconds):
    cache = {}
    locks = {}

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Convert all elements in args and kwargs to be hashable
            hashable_args = tuple(make_hashable(arg) for arg in args)
            hashable_kwargs = tuple(sorted((k, make_hashable(v)) for k, v in kwargs.items()))
            key = (hashable_args, hashable_kwargs)
            # Check if the cached value exists and is not expired
            if key in cache:
                value, timestamp = cache[key]
                if time.time() - timestamp < max_age_seconds:
                    return value
            # If a lock does not exist for the key, create one
            if key not in locks:
                locks[key] = threading.Lock()
            # Use the lock to ensure only one thread recomputes the value
            with locks[key]:
                # Check the cache again to avoid recomputing if another thread already did it
                if key in cache:
                    value, timestamp = cache[key]
                    if time.time() - timestamp < max_age_seconds:
                        return value
                # Compute and cache the new value
                value = func(*args, **kwargs)
                cache[key] = (value, time.time())
                return value

        def clear_cache():
            cache.clear()
            locks.clear()
            logging.info('Cache cleared on function: %s', func.__name__)

        wrapper.clear_cache = clear_cache
        return wrapper
    return decorator

# Example usage
CACHE_TIMEOUT = 6000  # Example cache timeout in seconds
