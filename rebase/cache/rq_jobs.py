from functools import partial

from flask import current_app
from requests import post

def action(name, role_id):
    current_app.default_queue.enqueue(
        post,
        'http://{cache}/{action}/{role_id}'.format(
            cache=current_app.config['CACHE_HOST'],
            action=name,
            role_id=role_id
        )
    )

warmup = partial(action, 'warmup')
cooldown = partial(action, 'cooldown')
