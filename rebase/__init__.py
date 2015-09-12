import sys
from os import environ

from flask import Flask, request
from flask.ext.restful import Api
from flask_debugtoolbar import DebugToolbarExtension

from rebase.common.routes import register_routes
from rebase.common.database import DB, DB_PRODUCTION_NAME
from rebase.github.routes import register_github_routes
from rebase.home.routes import register_home
from rebase.setup.rq import setup_rq
from rebase.setup.login import setup_login
from rebase.setup.admin import setup_admin
from rebase.setup.cache import setup_cache

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
    if testing:
        # WARNING: be sure to close the pipe when exiting this process!
        setattr(app, 'fifo_db', fifo_db = open('/tmp/db', 'r'))
        db_url = app.fifo_db.read()
        print(db_url)
    else:
        db_url = environ['DATABASE_URL']
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    setup_admin(app, DB.session)
    setup_login(app)
    setup_rq(app)
    setup_cache(app)
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
