
from .config import config as base_config

# treat the base_config as immutable

config = dict(base_config)

# To extend or modify inherited settings:

#config.update({
    #'FOO': 'BAR',
#})


