#! /venv/rq_p2/bin/python


from logging import Formatter, getLogger, DEBUG
from logging.handlers import SysLogHandler
from multiprocessing import current_process
from signal import signal, SIGTERM, SIGQUIT, SIGINT
from sys import argv, exit, stdin, stdout, stderr
from time import sleep

from msgpack import unpackb

from rebase.skills.python import PythonScanner

logger = getLogger()


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


def quit(sig, frame):
    logger.debug('Received signal: %s', sig)
    exit(-sig)


def main(argv):
    signal(SIGTERM, quit)
    signal(SIGQUIT, quit)
    signal(SIGINT, quit)
    current_process().name = 'Python 2 Scanner'
    logger.setLevel(DEBUG)
    rsyslog = SysLogHandler(('rsyslog', 514))
    rsyslog.setFormatter(Formatter('%(levelname)s {%(processName)s[%(process)d]} %(message)s'))
    logger.addHandler(rsyslog)
    logger.debug('Listening to stdin for messages.')
    while True:
        next_object_length = int(stdin.readline().strip('\n'))
        #logger.debug('length: %d', next_object_length)
        obj = unpackb(stdin.read(next_object_length))
        logger.debug('object: %s', obj)


if __name__ == '__main__':
    try:
        main(argv)
    except ParserException as e:
        logger.warning(e.message)
        exit(e.code)

