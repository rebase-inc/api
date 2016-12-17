
from .config import config as parent_config

# do not modify the parent config:
config = dict(parent_config)

# put here settings that are specific for 'web' for this installation

config.update({
    'APP_URL': 'https://alpha.rebaseapp.com',
    'CODE2RESUME_URL': 'https://code2resume.rebaseapp.com',
})
