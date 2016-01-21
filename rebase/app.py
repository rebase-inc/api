from os import environ

from flask import Flask
from flask.ext.restful import Api
from flask_debugtoolbar import DebugToolbarExtension

from rebase.common.exceptions import errors
from rebase.common.env import check
from rebase.github.routes import register_github_routes
from rebase.home.routes import register_home
from rebase.features import install


def create(testing=False):
    '''
    Use create_app when you need an app to interact with the database
    or Flask at a very low level and basically don't really care abot the routes and widgets.
    Example: in the parsers, in run-workers.
    '''
    # TODO: check whether we're still using 'testing'
    if testing:
        check(['TEST_URL'])
    app = Flask(__name__, static_url_path='')
    app_context = app.app_context()
    app_context.push()
    app.config.from_object('rebase.common.config.Config')
    app.config.from_envvar('APP_SETTINGS')
    from rebase.common.database import DB
    DB.init_app(app)
    toolbar = DebugToolbarExtension(app)

    install(app)
    api = Api(app, prefix=app.config['URL_PREFIX'], errors=errors)
    register_home(app)
    # some routes use flask.ext.cache is can't be created until an app and its context exist
    from rebase.common.routes import register_routes
    register_routes(api)
    register_github_routes(app)
    return app, app_context, DB
