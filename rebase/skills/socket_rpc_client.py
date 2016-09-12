from functools import partialmethod, partial
from json import loads, dumps
from logging import getLogger
from socket import socket, SHUT_RDWR
from zlib import compress


logger = getLogger(__name__)


FRAME_SIZE_MAX = 2*1024*1024


class FrameSizeExceeded(Exception):

    msg = partial('Frame size ({size}) exceeds limit of {MAX} bytes'.format, MAX=FRAME_SIZE_MAX)

    def __init__(size):
        self.message = msg(size=size)


class SocketRPCClient(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket()
        self.read_stream = self.socket.makefile()
        self.write_stream = self.socket.makefile(mode='w')
        self.socket.connect((self.host, self.port))

    def close(self):
        self.socket.shutdown(SHUT_RDWR)
        self.read_stream.close()
        self.write_stream.close()
        self.socket.close()

    def remote_procedure_call(self, method, *args, dumps_kw=None, loads_kw=None):
        frame = dumps(
                [method, *args],
                **(dumps_kw if dumps_kw else dict())
        )
        frame_size = len(frame)
        if  frame_size > FRAME_SIZE_MAX:
            raise FrameSizeExceeded(frame_size)
        self.write_stream.write(frame)
        self.write_stream.write('\n')
        self.write_stream.flush()
        return loads(self.read_stream.readline(), **(loads_kw if loads_kw else dict()))


def method(id_):
    return partialmethod(SocketRPCClient.remote_procedure_call, id_)


