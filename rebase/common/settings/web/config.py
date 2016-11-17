from os import environ

from ..all_services import config as root_config

config = dict(root_config)

# put here all the settings specific to the 'web' service
# but shared between all installations ('dev', 'pro', 'my_install', etc.).

config.update({
    'GITHUB_APP_ID':                environ['GITHUB_APP_ID'],
    'GITHUB_APP_SECRET':            environ['GITHUB_APP_SECRET'],
    'GITHUB_CODE2RESUME_ID':        environ['GITHUB_CODE2RESUME_ID'],
    'GITHUB_CODE2RESUME_SECRET':    environ['GITHUB_CODE2RESUME_SECRET'],
})
