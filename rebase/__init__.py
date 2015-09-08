import sys
from os import environ, urandom

from flask import Flask, request
from flask.ext.restful import Api
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask.ext.sqlalchemy import SQLAlchemy

from rebase.common.routes import register_routes
from rebase.common.database import DB, DB_PRODUCTION_NAME
from rebase.github.routes import register_github_routes
from rebase.home.routes import register_home
from rebase.setup.rq import setup_rq
from rebase.setup.login import setup_login
from rebase.setup.admin import setup_admin
from rebase.setup.cache import setup_cache

sys.dont_write_bytecode = True

def create_app(testing=False):
    """ Create our app using the Flask factory pattern """
    if 'DATABASE_URL' not in environ or 'APP_SETTINGS' not in environ:
        raise EnvironmentError('Missing environment variables. Did you forget to run "source setup.sh" or "source test_setup.sh"?')
    app = Flask(__name__)
    app.secret_key = urandom(24)
    app.config.from_object(environ['APP_SETTINGS'])
    app_context = app.app_context()
    app_context.push()
    toolbar = DebugToolbarExtension(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = environ['TEST_URL'] if testing else environ['DATABASE_URL']
    setup_admin(app, DB.session)
    setup_login(app)
    setup_rq(app)
    setup_cache(app)
    DB.init_app(app)
    api = Api(app)
    register_home(app)
    register_routes(api)
    register_github_routes(app)

    @app.after_request
    def add_cors(resp):
        """ Ensure all responses have the CORS headers. This ensures any failures are also accessible
        by the client. """
        resp.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin','*')
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Access-Control-Allow-Methods'] = 'PUT, POST, OPTIONS, GET'
        resp.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', 'Authorization' )
        # set low for debugging
        if app.debug:
            resp.headers['Access-Control-Max-Age'] = '1000'
        return resp

    return app, app_context, DB
