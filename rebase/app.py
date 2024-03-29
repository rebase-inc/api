from os import environ

from flask import Flask

from .common.env import check


def basic_app():
    app = Flask(__name__, static_url_path='')
    app.config.from_object('rebase.common.config')
    return app


def create(routes=False):
    '''
    Use 'create' when you need an app to interact with the database
    or Flask at a very low level and basically don't really care abot the routes and widgets.
    Example: in the parsers, in run-workers.
    Note: calling 'create' resets the global variable 'rebase.common.database.DB',
    making it safe to use within an 'app context'.
    '''
    from flask_restful import Api
    from rebase.common.database import DB
    from rebase.common.exceptions import errors
    from rebase.features.install import install
    app = basic_app()
    install(app)
    DB.init_app(app)
    api = Api(app, prefix=app.config['API_URL_PREFIX'], errors=errors)
    if routes:
        # some routes use flask_cache is can't be created until an app and its context exist
        with app.app_context():
            from rebase.common.routes import register_routes
            from rebase.github.routes import register_github_routes
            register_routes(api)
            register_github_routes(app)
    return app


