from logging import getLogger
from traceback import format_stack


logger = getLogger()


def dump_stack():
    bunch_of_lines = format_stack()
    for line in bunch_of_lines:
        for _line in line.splitlines():
            logger.debug(line)


