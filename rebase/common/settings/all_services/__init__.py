from importlib import import_module
from os import environ


config = import_module(environ['ALL_SERVICES_SETTINGS'], package='rebase.common.settings.all_services').config


