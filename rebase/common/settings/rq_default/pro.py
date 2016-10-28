from logging import INFO
from os import environ

from .config import config as base_config


config = dict(base_config)


config.update({
    'BACKEND_AWS_ACCESS_KEY_ID':        environ['BACKEND_AWS_ACCESS_KEY_ID'],
    'BACKEND_AWS_SECRET_ACCESS_KEY':    environ['BACKEND_AWS_SECRET_ACCESS_KEY'],
    'LOG_LEVEL': INFO,
})


