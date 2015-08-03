import sys
from os import environ

from flask.ext.restful import Api
from flask.ext.login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from alveare.common.routes import register_routes
from alveare.models import User
from alveare.common.database import DB, DB_PRODUCTION_NAME

sys.dont_write_bytecode = True

def create_admin_page(app):
    admin = Admin(app, name='Rebase', template_mode='bootstrap3')
    admin.add_view(ModelView(User, DB.session))


def create_app():
    """ Create our app using the Flask factory pattern """
    app = Flask(__name__)
    app.config.from_object(environ['APP_SETTINGS'])
    app_context = app.app_context()
    app_context.push()
    create_admin_page(app)
    if 'DATABASE_URL' in environ:
        app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL']
    else:
        raise EnvironmentError('You need to set the DATABASE_URL variable in your environment. Did you forget to run "source setup.sh" or "source test_setup.sh"?')

    class AnonymousUser(object):
        is_active = False
        def is_authenticated(self): return False
        def is_anonymous(self): return True
        def get_id(self): return None
        def allowed_to_get(self, instace): return False
        def allowed_to_create(self, instance): return isinstance(instance, User)
        def allowed_to_modify(self, instance): return False
        def allowed_to_delete(self, instance): return False
    login_manager = LoginManager()
    login_manager.anonymous_user = AnonymousUser
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    DB.init_app(app)
    api = Api(app)
    register_routes(api)
    app.secret_key = 'Not really secret'
    return app, app_context, DB

