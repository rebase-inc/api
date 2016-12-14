from base64 import b64decode
from contextlib import contextmanager
from functools import partial
from inspect import getargspec
from logging import getLogger
from multiprocessing import current_process
from signal import signal, SIGTERM, SIGQUIT, SIGINT
from sys import argv, exit
from time import sleep

from rebase.common.log import setup as log_setup
from rebase.skills.importable_modules import ImportableModules
from rebase.skills.python_client import PythonClient
from rebase.skills.scanner_client import ScannerClient
from rebase.subprocess import create_json_streaming_server
from rebase.subprocess.exceptions import SubprocessException


log_setup()


logger = getLogger(__name__)


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


def quit(sig, frame, transport):
    transport.close()
    logger.debug('Received signal: %s', sig)
    exit(-sig)


def validate_object(object_, methods):
    if 'method' not in object_ or 'args' not in object_:
        raise InvalidMethodCall()
    method = object_['method']
    if method not in methods:
        raise InvalidMethod()
    args = object_['args']
    if args:
        # +1 for self parameter
        if len(object_['args'])+1 != methods[method]:
            raise InvalidMethodArguments()
    else:
        if 1 != methods[method]:
            raise InvalidMethodArguments()


scanner_methods = {
    fn.__name__: len(getargspec(fn)[0]) for fn in (
        ScannerClient.languages,
        ScannerClient.grammar,
        ScannerClient.scan_contents,
    )
}


validate = partial(validate_object, methods=scanner_methods)


def setup(transport):
    quit_ = partial(quit, transport=transport)
    signal(SIGTERM, quit_)
    signal(SIGQUIT, quit_)
    signal(SIGINT, quit_)
    current_process().name = 'Python 2 Client'
    logger.debug('setup completed')


def instance_method_call(instance, method_call):
    # uncomment 'validate' when debugging
    # TODO should we use PYTHONDEBUG in environment instead?
    # validate(method_call)
    args = method_call['args']
    if args:
        return getattr(instance, method_call['method'])(*method_call['args'])
    return getattr(instance, method_call['method'])()


class Python2Client(PythonClient):
    '''
        Thin wrapper to re-encode the context as an ImportableModules object.
        While traveling through the input pipe, the ImportableModules object was encoded as a JSON Array.
    '''

    def scan_contents(self, language_index, filename, code, importable_modules_as_list):
        return super(Python2Client, self).scan_contents(
            language_index,
            filename,
            b64decode(code),
            frozenset(importable_modules_as_list)
        )


python_client_call = partial(instance_method_call, Python2Client())


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
def exit_on_error(transport):
    try:
        yield
    except SubprocessException as e:
        logger.exception('in parse_python2.py, SubprocessException caught in parse_python2.py')
        transport.close()
        exit(1)
    except Exception as last_chance:
        logger.exception('in parse_python2.py, Uncaught exception in parse_python2.py')
        transport.close()
        exit(2)
    else:
        transport.close()
        exit(0)


def main():
    try:
        transport, protocol = create_json_streaming_server(argv[1])
        setup(transport)
        with exit_on_error(transport):
            protocol.run_forever(python_client_call, handle_errors)
    except ParserException as e:
        logger.warning(e.message)
        exit(e.code)


if __name__ == '__main__':
    main()


