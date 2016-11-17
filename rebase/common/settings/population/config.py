from os import environ

from ..all_services import config as root_config

# Settings that are common to all derived settings,
# typically the dictionary declared in dev.py (for development) or pro.py (for production).

# treat the root config as immutable

config = dict(root_config)


config.update({
    'S3_BUCKET': environ['S3_BUCKET']
})


