import sys

from flask.ext.restful import Api
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from alveare.common.routes import register_routes

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
    sqlalchemy_object.init_app(app)
    api = Api(app)
    register_routes(api)
    return app

