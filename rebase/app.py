from logging import getLogger
from os import environ

from flask import Flask, _app_ctx_stack
from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

from rebase.common.database import DB
from rebase.common.exceptions import errors
from rebase.common.env import check
from rebase.home.routes import register_home
from rebase.features import install


def create(testing=False):
    '''
    Use 'create' when you need an app to interact with the database
    or Flask at a very low level and basically don't really care abot the routes and widgets.
    Example: in the parsers, in run-workers.
    Note: calling 'create' resets the global variable 'rebase.common.database.DB',
    making it safe to use within an 'app context'.
    '''
    app = Flask(__name__, static_url_path='')
    app.config.from_object('rebase.common.config.Config')
    app.config.from_envvar('APP_SETTINGS')
    toolbar = DebugToolbarExtension(app)

    install(app)
    logger = getLogger()
    logger.debug('create, before first app_context is create, stack top: %s', _app_ctx_stack.top)
    api = Api(app, prefix=app.config['URL_PREFIX'], errors=errors)
    register_home(app)
    # some routes use flask.ext.cache is can't be created until an app and its context exist
    with app.app_context():
        from rebase.common.routes import register_routes
        from rebase.github.routes import register_github_routes
        register_routes(api)
        register_github_routes(app)
    # note: exiting the app_context will close the underlying SQLAlchemy session in DB
    # so we need to recreate DB.
    # Additionally, this allows multiple calls to 'create' to reset the global variable DB,
    # which allows us to share code between processes that use app contexts implicitly (web request processes, a.k.a. gunicorn workers)
    # versus long-running processes that are not bound a particular HTTP request (RQ workers, scheduler, cache, etc.)
    DB = SQLAlchemy()
    DB.init_app(app)
    logger.debug('create, after DB.init_app, stack top: %s', _app_ctx_stack.top)
    return app


