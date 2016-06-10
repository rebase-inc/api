from logging import getLogger
from traceback import format_stack


logger = getLogger()


def dump_stack():
    big_string = format_stack()
    for line in big_string.splitlines():
        logger.debug(line)


