from os import environ

from .config import config as parent_config


config = dict(parent_config)


config.update({
    'BACKEND_AWS_ACCESS_KEY_ID': 'AKIAIXI7F5KZC7UOG5VQ',
    'BACKEND_AWS_SECRET_ACCESS_KEY': '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',
    'LOG_LEVEL': 'DEBUG',
    'S3_BUCKET': environ['S3_BUCKET'],
})


