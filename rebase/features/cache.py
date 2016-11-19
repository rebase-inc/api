from collections import defaultdict

from flask_cache import Cache


def setup_cache(app):
    redis = Cache(
        app, 
        config = {
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_HOST': app.config['REDIS_HOST']
        }
    )
    setattr(app, 'redis', redis)

    in_process = Cache(
        app, 
        config = {
            'CACHE_TYPE': 'simple',
            'CACHE_DEFAULT_TIMEOUT': 3600,
            'CACHE_THRESHOLD': 10000,
        }
    )
    setattr(in_process, 'keys', defaultdict(set))
    setattr(in_process, 'misses', 0)
    setattr(app, 'cache_in_process', in_process)
