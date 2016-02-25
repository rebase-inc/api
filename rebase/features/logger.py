from logging import Formatter, getLogger
from logging.handlers import SysLogHandler



def has_syslog(logger):
    found = False
    for handler in logger.handlers:
        if isinstance(handler, SysLogHandler):
            found = True
            break
    return found


def setup(logger, level, syslog_address, format_str):
    logger.setLevel(level)
    if not has_syslog(logger):
        rsyslog = SysLogHandler(syslog_address)
        rsyslog.setFormatter(Formatter(format_str))
        logger.addHandler(rsyslog)


def setup_with_conf(logger, basic, syslog):
    setup(logger, basic['level'], syslog['address'], basic['format'])


def setup_logger(app):
    logger = getLogger()
    setup_with_conf(logger, app.config['BASIC_LOG_CONFIG'], app.config['RSYSLOG_CONFIG'])


