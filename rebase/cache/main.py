from logging import info, debug, error
from queue import Queue, Empty

from rebase.cache.app import create


def cache_main(role_id, q, name):
    info('Started child process')
    app, _, db = create()
    # create a fake request context to allow flask.ext.login to work
    # which is needed wherever 'current_user' is read
    ctx = app.test_request_context('/foobar')
    ctx.push()
    while True:
        try:
            task = q.get(timeout=3600)
        except Empty as e:
            info('TIMEOUT')
            break
        debug('Received: {}'.format(task))
        function, args, kwargs = task['action']
        function(role_id, *args, **kwargs)
    info('Exiting child process')
