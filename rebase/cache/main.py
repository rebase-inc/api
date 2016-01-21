from queue import Queue, Empty

from rebase.cache.tasks import warmup

def cache_main(user_role_id, q, name):
    app, _, db = create()
    for user in User.query.all():
        print('User: {}'.format(user))
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
            warmup(app, db, user_role_id)
