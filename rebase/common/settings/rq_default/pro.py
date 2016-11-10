from os import environ

from .config import config as base_config


config = dict(base_config)


# to extend or modifying:

config.update({
    'CRAWLER_USERNAME': environ['CRAWLER_USERNAME'],
    'CRAWLER_PASSWORD': environ['CRAWLER_PASSWORD']
})


