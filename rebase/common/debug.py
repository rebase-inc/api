from logging import getLogger
from pprint import pformat
from traceback import format_stack


logger = getLogger()


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
            logger.debug(line)


