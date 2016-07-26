from builtins import object, super
from functools import wraps
from logging import getLogger


logger = getLogger(__name__)


class InvalidState(Exception):
    message_format = 'Invalid State. Next state is {}, but {} was called instead'.format

    def __init__(self, next_state, state):
        super().__init__()
        self.message = self.message_format(next_state, state)


def next_state(expected_next_state):
    def method_decorator(method):
        @wraps(method)
        def new_method(self, *args, **kwargs):
            if self.next_state != method.__name__:
                raise InvalidState(self.next_state, method.__name__)
            result = method(self, *args, **kwargs)
            self.next_state = expected_next_state
            return result
        return new_method
    return method_decorator


class ClientProtocol(object):
    '''
        Launches a long-running subprocess that communicates synchronously over pipes
        Enforces a synchronous 

        Protocol:
        Client:             Server:
        -------------       ----------------------------------
        c1: write stdin     s1: read stdin
        c2: read  stderr    [do something with data received]
                            s2: write stderr
        c3: read stdout     s3: write stdout

        c4: loop c1         s4: loop s1
    '''

    def __init__(self, transport):
        self.transport = transport
        self.next_state = 'write_in'

    @next_state('read_err')
    def write_in(self, object_):
        return self.transport.write_in(object_)

    @next_state('read_out')
    def read_err(self):
        return self.transport.read_err()

    @next_state('write_in')
    def read_out(self):
        return self.transport.read_out()


class ServerProtocol(object):

    def __init__(self, transport):
        self.transport = transport
        self.next_state = 'read_in'

    @next_state('write_err')
    def read_in(self):
        object_ = self.transport.read_in()
        logger.debug('read_in: %s', object_)
        return object_

    @next_state('write_out')
    def write_err(self, err):
        if err:
            logger.debug('write_err: %s', err)
        self.transport.write_err(err)

    @next_state('read_in')
    def write_out(self, object_):
        logger.debug('write_out: %s', object_)
        return self.transport.write_out(object_)

    def run_once(self, on_new_input, on_error):
        object_ = self.read_in()
        try:
            result = on_new_input(object_)
        except Exception as e:
            logger.debug('caught exception while running on_new_input: %s', str(e))
            try:
                error = on_error(e)
                logger.debug('%s.run_once, on_error returned: %s', __name__, error)
                self.write_err(error)
            except Exception as e2:
                logger.debug('caught exception while running on_error: %s', str(e2))
                self.write_err(str(e2))
            finally:
                self.write_out(None)
        else:
            self.write_err(None)
            self.write_out(result)

    def run_forever(self, on_new_input, on_error):
        while True:
            self.run_once(on_new_input, on_error)

