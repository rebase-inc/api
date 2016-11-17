from os import environ

from ..all_services import config as root_config

# Settings that are common to all derived settings,
# typically the dictionary declared in dev.py (for development) or pro.py (for production).

# treat the root config as immutable

config = dict(root_config)

# to update:
# root_config.update({ 'FOO': 'BAR' })

config.update({
    'GITHUB_APP_ID':                environ['GITHUB_APP_ID'],
    'GITHUB_APP_SECRET':            environ['GITHUB_APP_SECRET'],
    'GITHUB_CODE2RESUME_ID':        environ['GITHUB_CODE2RESUME_ID'],
    'GITHUB_CODE2RESUME_SECRET':    environ['GITHUB_CODE2RESUME_SECRET'],
    'ONLY_THIS_REPO':               environ['ONLY_THIS_REPO'] if 'ONLY_THIS_REPO' in environ else None,
})


