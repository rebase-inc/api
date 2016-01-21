from flask.ext.cache import Cache
from flask.ext.login import current_app

def setup_cache(app):
    if getattr(app, 'cache', None):
        raise AttributeError('Flask app instance already has a \'cache\' attribute!')
    cache = Cache(
        current_app, 
        config = {
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_HOST': current_app.config['REDIS_HOST']
        }
    )
    setattr(app, 'cache', cache)
