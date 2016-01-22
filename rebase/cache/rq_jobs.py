from logging import debug
from pickle import dumps

from flask import current_app
from requests import post, delete

def prefix():
    return 'http://{cache}'.format(cache=current_app.config['CACHE_HOST'])

def role_url(role_id):
    return prefix()+'/role/'+str(role_id)

def warmup(role_id):
    current_app.default_queue.enqueue(post, role_url(role_id))

def cooldown(role_id):
    current_app.default_queue.enqueue(delete, role_url(role_id))

def invalidate(changeset):
    debug(changeset)
    current_app.default_queue.enqueue(post, prefix()+'/invalidate', data=dumps(tuple(changeset.keys())))
