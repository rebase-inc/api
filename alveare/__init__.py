import sys

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

sys.dont_write_bytecode = True

def create_app(database, config_filename = 'config'):
    """ Create our app using the Flask factory pattern """
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    #app.config.from_object(config_filename)
    database.init_app(app)
    return app

