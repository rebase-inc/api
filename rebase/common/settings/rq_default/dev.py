from os import environ as env

from .config import config as base_config

# treat the base_config as immutable

config = dict(base_config)

# To extend or modify inherited settings:

config.update({
    'CRAWLER_USERNAME': env['CRAWLER_USERNAME'],
    'CRAWLER_PASSWORD': env['CRAWLER_PASSWORD'],
    'REPOS_VOLUME_SIZE_IN_MB': int(env['REPOS_VOLUME_SIZE_IN_MB']),
    'CLONE_SIZE_SAFETY_FACTOR': int(env['CLONE_SIZE_SAFETY_FACTOR']),
})


