import sys

from flask.ext.restful import Api
from flask.ext.login import LoginManager
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from alveare.common.routes import register_routes
from alveare.models import User

sys.dont_write_bytecode = True

def create_app(sqlalchemy_object, database_type = 'sqlite', config_filename = 'config'):
    """ Create our app using the Flask factory pattern """
    app = Flask(__name__)
    if database_type == 'sqlite':
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    elif database_type == 'postgres':
        settings = dict(username='postgres', password='', host='localhost', port='5432', dbname='postgres')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{username}:{password}@{host}:{port}/{dbname}'.format(**settings)
    else:
        raise Exception('invalid database type!')
    #app.config.from_object(config_filename)
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

    sqlalchemy_object.init_app(app)
    api = Api(app)
    register_routes(api)
    app.secret_key = 'Not really secret'
    return app

