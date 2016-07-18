#! /venv/rq_p2/bin/python


from logging import Formatter, getLogger, DEBUG
from logging.handlers import SysLogHandler
from multiprocessing import current_process
from sys import argv, exit


class ParserException(Exception):
    error_message = 'ParserException base class message '
    message_format = '{error_message} {argv} exit: {code}'
    code = 255

    def __init__(self):
        self.message = self.message_format.format(
            error_message=self.error_message,
            argv=argv,
            code=self.code
        )


class MissingArguments(ParserException):
    error_message = 'Missing arguments'
    code = 1


def main(argv):
    current_process().name = 'parse_python2'
    logger = getLogger()
    logger.setLevel(DEBUG)
    rsyslog = SysLogHandler(('rsyslog', 514))
    rsyslog.setFormatter(Formatter('%(levelname)s {%(processName)s[%(process)d] %(threadName)s} %(message)s'))
    logger.addHandler(rsyslog)
    logger.debug('Booted.')


if __name__ == '__main__':
    try:
        main(argv)
    except ParserException as e:
        logger.warning(e.message)
        exit(e.code)

