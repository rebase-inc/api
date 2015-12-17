from os import environ

from flask import Flask
from flask.ext.restful import Api
from flask.ext.login import current_user
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug import secure_filename

from rebase.common.exceptions import errors
from rebase.common.env import check
from rebase.common.routes import register_routes
from rebase.github.routes import register_github_routes
from rebase.home.routes import register_home
from rebase.features import install


check(['APP_SETTINGS'])

def create_app(testing=False):
    '''
    Use create_app when you need an app to interact with the database
    or Flask at a very low level and basically don't really care abot the routes and widgets.
    Example: in the parsers, in run-workers.
    '''
    if testing:
        check(['TEST_URL'])
    app = Flask(__name__, static_url_path='')
    app_context = app.app_context()
    app_context.push()
    settings = environ['APP_SETTINGS']
    print('Using rebase configuration: '+settings)
    app.config.from_object(settings)
    from rebase.common.database import DB
    DB.init_app(app)
    toolbar = DebugToolbarExtension(app)

    install(app)
    api = Api(app, prefix=app.config['URL_PREFIX'], errors=errors)
    register_home(app)
    register_routes(api)
    register_github_routes(app)
    return app, app_context, DB
