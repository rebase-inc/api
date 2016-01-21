from queue import Queue, Empty

from rebase.cache.app import create
from rebase.cache.tasks import warmup
from rebase.models import (
    Role,
)

def cache_main(user_role_id, q, name):
    app, _, db = create()
    role = Role.query.get(user_role_id[1])
    if not role:
        print('Unknown role, terminating')
        return 1
    while True:
        try:
            task = q.get(timeout=600)
        except Empty as e:
            print('{} TIMEOUT'.format(name))
            break
        print('{} received: {}'.format(name, task))
        if task['action'] == 'QUIT':
            print('{} QUIT'.format(name, *user_role_id))
            break
        if task['action'] == 'warmup':
            warmup(app, db, role)
