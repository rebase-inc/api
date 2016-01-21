from queue import Queue, Empty

from flask.ext.login import login_user

from rebase.cache.app import create
from rebase.cache.tasks import warmup
from rebase.models import Role

def cache_main(role_id, q, name):
    app, _, db = create()
    role = Role.query.get(role_id)
    if not role:
        print('Unknown role, terminating')
        return 1
    role.user.set_role(role.id)
    # create a fake request context to allow flask.ext.login to work
    # which is needed wherever 'current_user' is read
    ctx = app.test_request_context('/foobar')
    ctx.push()
    login_user(role.user)
    while True:
        try:
            task = q.get(timeout=3600)
        except Empty as e:
            print('{} TIMEOUT'.format(name))
            break
        print('{} received: {}'.format(name, task))
        if task['action'] == 'cooldown':
            print('{} QUIT'.format(name))
            break
        if task['action'] == 'warmup':
            warmup(app, db, role)
