from logging import Formatter, getLogger
from logging.handlers import SysLogHandler


logger = getLogger()


def setup_logger(app):
    conf = app.config['BASIC_LOG_CONFIG']
    logger.setLevel(conf['level'])
    rsyslog = SysLogHandler(**app.config['RSYSLOG_CONFIG'])
    rsyslog.setFormatter(Formatter(conf['format']))
    logger.addHandler(rsyslog)


