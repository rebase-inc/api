from pickle import dumps

from flask import current_app
from requests import post, delete

from rebase.cache.model_ids import ModelIds


def prefix():
    return 'http://{cache}'.format(cache=current_app.config['CACHE_HOST'])

def role_url(role_id):
    return prefix()+'/role/'+str(role_id)

def warmup(role_id):
    current_app.default_queue.enqueue(post, role_url(role_id))

def cooldown(role_id):
    current_app.default_queue.enqueue(delete, role_url(role_id))

def invalidate(identity_map_keys):
    current_app.default_queue.enqueue(post, prefix()+'/invalidate', data=dumps(ModelIds(identity_map_keys)))
