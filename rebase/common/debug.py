from logging import getLogger
from pprint import pformat


logger = getLogger()


def pdebug(thing, header=None):
    logger.debug('\n')
    logger.debug('vvvvvvvvvvvvvvvv'+(' {} '.format(header) if header else '')+'vvvvvvvvvvvvvvvvv')
    for line in pformat(thing).splitlines():
        logger.debug(line)
    logger.debug('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')


