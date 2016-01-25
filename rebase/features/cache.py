from flask.ext.cache import Cache

def setup_cache(app):
    redis = Cache(
        app, 
        config = {
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_HOST': app.config['REDIS_HOST']
        }
    )
    setattr(app, 'cache_in_redis', redis)

    in_process = Cache(
        app, 
        config = {
            'CACHE_TYPE': 'simple',
        }
    )
    setattr(app, 'cache_in_process', in_process)
