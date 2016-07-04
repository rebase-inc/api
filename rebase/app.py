from logging import getLogger
from os import environ

from flask import Flask
from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy

from rebase.common.database import DB
from rebase.common.exceptions import errors
from rebase.common.env import check
from rebase.home.routes import register_home
from rebase.features import install


def create(routes=False):
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

    install(app)
    DB.init_app(app)
    logger = getLogger()
    api = Api(app, prefix=app.config['URL_PREFIX'], errors=errors)
    register_home(app)
    if routes:
        # some routes use flask.ext.cache is can't be created until an app and its context exist
        with app.app_context():
            from rebase.common.routes import register_routes
            from rebase.github.routes import register_github_routes
            register_routes(api)
            register_github_routes(app)
    return app


