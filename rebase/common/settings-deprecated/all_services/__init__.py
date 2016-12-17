from importlib import import_module
from logging import INFO
from os import environ


config = {
    'LOG_FORMAT': '%(levelname)s {%(processName)s[%(process)d]} %(message).900s',
    'LOG_LEVEL': INFO,
    'RSYSLOG_CONFIG': {
        'address': ('rsyslog', 514),
    },
}

