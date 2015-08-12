import sys
from os import environ

from flask import Flask, render_template
from flask.ext.restful import Api
from flask.ext.login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask.ext.sqlalchemy import SQLAlchemy

from rebase.common.routes import register_routes
from rebase.models import User
from rebase.common.database import DB, DB_PRODUCTION_NAME
from rebase.github.routes import register_github_routes

sys.dont_write_bytecode = True

def create_admin_page(app):
    admin = Admin(app, name='Rebase', template_mode='bootstrap3')
    admin.add_view(ModelView(User, DB.session))


class AnonymousUser(object):
    is_active = False
    def is_authenticated(self): return False
    def is_anonymous(self): return True
    def get_id(self): return None
    def allowed_to_get(self, instace): return False
    def allowed_to_create(self, instance): return isinstance(instance, User)
    def allowed_to_modify(self, instance): return False
    def allowed_to_delete(self, instance): return False

def create_app(testing=False):
    """ Create our app using the Flask factory pattern """
    if 'DATABASE_URL' not in environ or 'APP_SETTINGS' not in environ:
        raise EnvironmentError('Missing environment variables. Did you forget to run "source setup.sh" or "source test_setup.sh"?')
    app = Flask(__name__)
    app.config.from_object(environ['APP_SETTINGS'])
    app_context = app.app_context()
    app_context.push()
    create_admin_page(app)
    toolbar = DebugToolbarExtension(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = environ['TEST_URL'] if testing else environ['DATABASE_URL']
    login_manager = LoginManager()
    login_manager.anonymous_user = AnonymousUser
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    DB.init_app(app)
    api = Api(app)
    register_routes(api)
    register_github_routes(app)
    app.secret_key = 'Not really secret'

    @app.route('/')
    def login_root():
        return render_template('login.html')

    return app, app_context, DB
