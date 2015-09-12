from flask.ext.cache import Cache

def setup_cache(app):
    if getattr(app, 'cache', None):
        raise AttributeError('Flask app instance already has a \'cache\' attribute!')
    setattr(app, 'cache', Cache(app,config={'CACHE_TYPE': 'simple'}))
