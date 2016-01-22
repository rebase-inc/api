from functools import partial

from flask import current_app
from requests import post, delete


def url(role_id):
    return 'http://{cache}/role/{role_id}'.format(
        cache=current_app.config['CACHE_HOST'],
        role_id=role_id
    )

def warmup(role_id):
    current_app.default_queue.enqueue(post, url(role_id))

def cooldown(role_id):
    current_app.default_queue.enqueue(delete, url(role_id))
