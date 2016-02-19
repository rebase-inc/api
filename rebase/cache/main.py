import gc
from logging import info, debug, error
from queue import Queue, Empty
from sys import getsizeof

from flask import Flask, current_app
from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.routing import Map

from rebase.common.exceptions import errors
from rebase.features import install


def cache_main(role_id, q, name):
    info('Started child process')
    app = Flask(__name__, static_url_path='')
    app.config.from_object('rebase.common.config.Config')
    app.config.from_envvar('APP_SETTINGS')
    install(app)
    api = Api(app, prefix=app.config['URL_PREFIX'], errors=errors)
    from rebase.common.database import DB
    DB.init_app(app)
    routes_are_registered = False
    gc.disable()
    gc.collect()
    while True:
        with app.app_context():
            from rebase.common.routes import register_routes
            if not routes_are_registered:
                register_routes(api)
                routes_are_registered = True
            try:
                task = q.get(timeout=3600)
            except Empty as e:
                info('TIMEOUT')
                break
            #debug('Received: {}'.format(task))
            function, args, kwargs = task['action']
            # create a fake request context to allow flask.ext.login to work
            # which is needed wherever 'current_user' is read
            with app.test_request_context('/foobar'):
                function(current_app, role_id, *args, **kwargs)
                debug('# of cache keys: %d', len(current_app.cache_in_process.keys))
                debug('Size of cache keys: %d bytes', getsizeof(current_app.cache_in_process.keys))
        # Run the garbage collection after each 'function' call
        # This speeds up the function call by 20%.
        gc.collect()
    info('Exiting child process')


