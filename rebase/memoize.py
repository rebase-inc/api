from flask.ext.cache import Cache
from flask.ext.login import current_app


redis = Cache(
    current_app, 
    config = {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_HOST': current_app.config['REDIS_HOST']
    }
)

in_process = Cache(
    current_app, 
    config = {
        'CACHE_TYPE': 'simple',
    }
)
