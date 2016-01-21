
from flask import Flask
from flask.ext.restful import Api

from rebase.common.exceptions import errors
from rebase.common.routes import register_routes
from rebase.features import install


def create():
    '''
    Creates an app that caches slow routes from the regular app.
    cache has its own routes to allow the web service to tell which pieces of data to invalidate.
    Cached data is stored on Redis. The web service reads the cache data directly from Redis.
    The slow routes, corresponding to Tickets, Auctions, Work, Completed on the Client, are computed together.
    For a given user, these routes share a lot of data, so computing them together re-uses the in-process cache
    which makes the computation much faster and uses far less memory.
    '''
    app = Flask(__name__, static_url_path='')
    app_context = app.app_context()
    app_context.push()
    app.config.from_object('rebase.common.config.Config')
    app.config.from_envvar('APP_SETTINGS')
    from rebase.common.database import DB
    DB.init_app(app)
    install(app)
    api = Api(app, prefix=app.config['URL_PREFIX'], errors=errors)
    register_routes(api)
    return app, app_context, DB
