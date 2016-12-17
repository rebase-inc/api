from os import environ

from ..all_services import config as root_config

config = dict(root_config)

config.update({
    'GITHUB_APP_CLIENT_ID':                environ['GITHUB_APP_CLIENT_ID'],
    'GITHUB_APP_CLIENT_SECRET':            environ['GITHUB_APP_CLIENT_SECRET'],
})
