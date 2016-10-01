from importlib import import_module
from os import environ


config = import_module(environ['SETTINGS'], package='rebase.common.settings').config


