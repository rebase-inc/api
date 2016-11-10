from logging import getLogger, Formatter
from logging.handlers import SysLogHandler

from .debug import pinfo
from .settings import config


def setup():
    root_logger = getLogger()
    root_logger.setLevel(config['LOG_LEVEL'])
    rsyslog = SysLogHandler(**config['RSYSLOG_CONFIG'])
    rsyslog.setFormatter(Formatter(config['LOG_FORMAT']))
    root_logger.addHandler(rsyslog)
    root_logger.debug('Root logger is setup')


def print_config():
    pinfo(config, '---- Service Config ----')


