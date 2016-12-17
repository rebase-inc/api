from functools import partial
from logging import getLogger, Formatter
from logging.handlers import SysLogHandler
from pprint import pformat
from sys import prefix, exec_prefix
from traceback import format_stack



logger = getLogger(__name__)


def multiline(level_fn, thing, header=None):
    logger.debug('\n')
    logger.debug('vvvvvvvvvvvvvvvv'+(' {} '.format(header) if header else '')+'vvvvvvvvvvvvvvvvv')
    for line in pformat(thing).splitlines():
        logger.debug(line)
    logger.debug('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

pdebug = partial(multiline, logger.debug)
pinfo = partial(multiline, logger.info)
pwarning = partial(multiline, logger.warning)


def dump_stack():
    bunch_of_lines = format_stack()
    for line in bunch_of_lines:
        for _line in line.splitlines():
            logger.debug(_line)


def setup_log_to_file(path):
    from logging import FileHandler
    logger = getLogger()
    logger.addHandler(FileHandler(path))
    return logger


