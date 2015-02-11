import sys

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

sys.dont_write_bytecode = True

from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def create_app(database, config_filename = 'config'):
    """ Create our app using the Flask factory pattern """
    app = Flask(__name__)
    settings = dict(username='postgres', password='', host='localhost', port='5432', dbname='postgres')
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{username}:{password}@{host}:{port}/{dbname}'.format(**settings)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    #app.config.from_object(config_filename)
    database.init_app(app)
    return app

