import gc
from logging import getLogger
from queue import Queue, Empty
from sys import getsizeof

from flask import Flask, current_app
from flask_restful import Api

from rebase.common.exceptions import errors
from rebase.features.install import install


logger = getLogger()


def cache_main(role_id, q, name):
    app = Flask(__name__, static_url_path='')
    app.config.from_object('rebase.common.config.Config')
    install(app)
    logger.info('Started child process')
    api = Api(app, prefix=app.config['API_URL_PREFIX'], errors=errors)
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
                task = q.get()
            except Empty as e:
                logger.info('TIMEOUT')
                break
            #logger.debug('Received: {}'.format(task))
            function, args, kwargs = task['action']
            # create a fake request context to allow flask_login to work
            # which is needed wherever 'current_user' is read
            with app.test_request_context('/foobar'):
                function(current_app, role_id, *args, **kwargs)
                logger.debug('# of cache keys: %d', len(current_app.cache_in_process.keys))
                logger.debug('Size of cache keys: %d bytes', getsizeof(current_app.cache_in_process.keys))
        # Run the garbage collection after each 'function' call
        # This speeds up the function call by 20%.
        gc.collect()
    logger.info('Exiting child process')


