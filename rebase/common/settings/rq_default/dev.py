from os import environ

from .config import config as base_config

# treat the base_config as immutable

config = dict(base_config)

# To extend or modify inherited settings:

config.update({
    'CRAWLER_USERNAME': environ['CRAWLER_USERNAME'],
    'CRAWLER_PASSWORD': environ['CRAWLER_PASSWORD'],
})


