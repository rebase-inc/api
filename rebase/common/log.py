from logging import getLogger, Formatter, DEBUG, StreamHandler
from logging.handlers import SysLogHandler
from sys import stdout

from .debug import pinfo


def setup():
    from .settings import config
    root_logger = getLogger()
    root_logger.setLevel(config['LOG_LEVEL'])
    rsyslog = SysLogHandler(**config['RSYSLOG_CONFIG'])
    rsyslog.setFormatter(Formatter(config['LOG_FORMAT']))
    root_logger.addHandler(rsyslog)
    root_logger.debug('Root logger is setup')


def print_config():
    from .settings import config
    pinfo(config, '---- Service Config ----')


def log_to_stdout():
    root_logger = getLogger()
    root_logger.setLevel(DEBUG)
    streamingHandler = StreamHandler(stdout)
    streamingHandler.setFormatter(Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(streamingHandler)

