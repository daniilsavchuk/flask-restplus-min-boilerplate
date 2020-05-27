from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options


EXPIRE_CACHE = 3600


cache_opts = {
    'cache.type': 'memory', # could be ext:redis
    'cache.lock_dir': './lock'
    # 'cache.url' : 'redis://localhost:6379'
}

cache = CacheManager(**parse_cache_config_options(cache_opts))


def invalidate_all_cache():
    cache_names = cache.get_cache('').namespace.namespaces.dict.keys()
    for cache_name in cache_names:
        cache.get_cache(cache_name).clear()
