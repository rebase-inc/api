from os import environ

from flask import Flask
from flask.ext.restful import Api
from flask_debugtoolbar import DebugToolbarExtension

from rebase.common.routes import register_routes
from rebase.common.database import DB, DB_PRODUCTION_NAME
from rebase.github.routes import register_github_routes
from rebase.home.routes import register_home
import rebase.models
from rebase.features import install

def create_app(testing=False):
    """ Create our app using the Flask factory pattern """
    if 'DATABASE_URL' not in environ or 'APP_SETTINGS' not in environ:
        raise EnvironmentError('Missing environment variables. Did you forget to run "source setup.sh" or "source test_setup.sh"?')
    app = Flask(__name__)
    app_context = app.app_context()
    app_context.push()
    DB.init_app(app)
    app.config.from_object(environ['APP_SETTINGS'])
    toolbar = DebugToolbarExtension(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = environ['TEST_URL'] if testing else environ['DATABASE_URL']
    #print('Database URL: {}'.format(app.config['SQLALCHEMY_DATABASE_URI']))
    install(app)
    api = Api(app)
    register_home(app)
    register_routes(api)
    register_github_routes(app)

    return app, app_context, DB
