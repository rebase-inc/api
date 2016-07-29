from logging import getLogger
from pprint import pformat
from sys import prefix, exec_prefix
from traceback import format_stack


logger = getLogger(__name__)


def pdebug(thing, header=None):
    logger.debug('\n')
    logger.debug('vvvvvvvvvvvvvvvv'+(' {} '.format(header) if header else '')+'vvvvvvvvvvvvvvvvv')
    for line in pformat(thing).splitlines():
        logger.debug(line)
    logger.debug('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')


def dump_stack():
    bunch_of_lines = format_stack()
    for line in bunch_of_lines:
        for _line in line.splitlines():
            logger.debug(_line)


def setup_rsyslog():
    from rebase.common.config import Config
    from logging import getLogger, Formatter
    from logging.handlers import SysLogHandler
    conf = Config.BASIC_LOG_CONFIG
    logger = getLogger()
    logger.setLevel(conf['level'])
    rsyslog = SysLogHandler(**Config.RSYSLOG_CONFIG)
    rsyslog.setFormatter(Formatter(conf['format']))
    logger.addHandler(rsyslog)
    return logger

def setup_log_to_file(path):
    from logging import FileHandler
    logger = getLogger()
    logger.addHandler(FileHandler(path))
    return logger


