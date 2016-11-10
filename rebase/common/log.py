from logging import getLogger, Formatter
from logging.handlers import SysLogHandler


logger = getLogger(__name__)


def setup():
    from rebase.common.settings import config
    logger_ = getLogger()
    logger_.setLevel(config['LOG_LEVEL'])
    rsyslog = SysLogHandler(**config['RSYSLOG_CONFIG'])
    rsyslog.setFormatter(Formatter(config['LOG_FORMAT']))
    logger_.addHandler(rsyslog)
    logger.debug('Logger is setup')
    return logger_


