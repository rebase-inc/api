#! /venv/rq_p2/bin/python

from contextlib import contextmanager
from functools import partial
from inspect import getargspec
from logging import getLogger
from multiprocessing import current_process
from signal import signal, SIGTERM, SIGQUIT, SIGINT
from sys import argv, exit
from time import sleep

from rebase.common.debug import setup_rsyslog
from rebase.skills.python import PythonScanner
from rebase.skills.tech_profile import ExposureEncoder
from rebase.skills.technology_scanner import TechnologyScanner
from rebase.subprocess import create_json_streaming_server
from rebase.subprocess.exceptions import SubprocessException


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


class InvalidMessage(ParserException):
    error_message = 'Invalid message'
    code = 1


class InvalidMethod(ParserException):
    error_message = 'Invalid method'
    code = 2


class InvalidMethodArguments(ParserException):
    error_message = 'Invalid method arguments'
    code = 3

def quit(sig, frame):
    logger.debug('Received signal: %s', sig)
    exit(-sig)


def validate_object(object_, methods):
    if 'method' not in object_ or 'args' not in object_:
        raise InvalidMethodCall()
    method = object_['method']
    if method not in methods:
        raise InvalidMethod()
    # +1 for self parameter
    if len(object_['args'])+1 != methods[method]:
        raise InvalidMethodArguments()


scanner_methods = { fn.__name__: len(getargspec(fn)[0]) for fn in (TechnologyScanner.scan_contents, TechnologyScanner.scan_patch) }


validate = partial(validate_object, methods=scanner_methods)


def setup():
    signal(SIGTERM, quit)
    signal(SIGQUIT, quit)
    signal(SIGINT, quit)
    current_process().name = 'Python 2 Scanner'
    setup_rsyslog()
    logger.debug('setup completed')


def instance_method_call(instance, method_call):
    validate(method_call)
    return getattr(instance, method_call['method'])(*method_call['args'])

python_scanner_call = partial(instance_method_call, PythonScanner())


def handle_errors(exception_):
    if isinstance(exception_, SyntaxError):
        return (0, {
            'filename': exception_.filename,
            'lineno':   exception_.lineno,
            'offset':   exception_.offset,
            'text':     exception_.text
        })
    else:
        return (1, str(exception_))


@contextmanager
def exit_on_error():
    try:
        yield
    except SubprocessException as e:
        logger.warning('%s', e)
        exit(1)
    else:
        exit(0)

def main(argv):
    setup()
    transport, protocol = create_json_streaming_server(
        argv[1],
        dumps_kwargs= {
            'cls': ExposureEncoder
        }
    )
    with exit_on_error():
        protocol.run_forever(python_scanner_call, handle_errors)


if __name__ == '__main__':
    try:
        main(argv)
    except ParserException as e:
        logger.warning(e.message)
        exit(e.code)

