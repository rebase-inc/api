from logging import info, debug, error
from queue import Queue, Empty

from flask.ext.sqlalchemy import SQLAlchemy

from rebase.cache.app import create


def cache_main(role_id, q, name):
    info('Started child process')
    app = create()
    # create a fake request context to allow flask.ext.login to work
    # which is needed wherever 'current_user' is read
    ctx = app.test_request_context('/foobar')
    ctx.push()
    from rebase.common.database import DB
    while True:
        DB = SQLAlchemy()
        DB.init_app(app)
        try:
            task = q.get(timeout=3600)
        except Empty as e:
            info('TIMEOUT')
            break
        debug('Received: {}'.format(task))
        function, args, kwargs = task['action']
        function(role_id, *args, **kwargs)
    info('Exiting child process')
