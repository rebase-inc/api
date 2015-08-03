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


def create_app(local=False, database_type = 'postgres', config_filename = 'config', db_name=DB_PRODUCTION_NAME):
    """ Create our app using the Flask factory pattern """
    app = Flask(__name__)
    app.config.from_object(environ['APP_SETTINGS'])
    app_context = app.app_context()
    app_context.push()
    create_admin_page(app)
    if database_type == 'sqlite':
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    elif database_type == 'postgres':
        if not local and 'DATABASE_URL' in environ:
            # DATABASE_URL is used by Heroku to advertise the location of the provisioned PostGreSQL DB.
            url = environ['DATABASE_URL']
        else:
            settings = dict(host='localhost', db_name=db_name)
            url = 'postgresql://{host}/{db_name}'.format(**settings)
        app.logger.debug('PostGresSQL URL: %s', url)
        app.config['SQLALCHEMY_DATABASE_URI'] = url
    else:
        raise Exception('invalid database type!')

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

