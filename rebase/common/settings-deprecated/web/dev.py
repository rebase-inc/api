from logging import DEBUG

from .config import config as parent_config

# do not modify the parent config:
config = dict(parent_config)

# put here settings that are specific for 'web' for this installation

config.update({
    'LOG_LEVEL': DEBUG,
    'APP_URL': 'http://dev:3000',
    'CODE2RESUME_URL': 'http://c2r:3001',
})


