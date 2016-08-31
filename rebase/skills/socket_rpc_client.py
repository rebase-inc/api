from functools import partialmethod
from json import loads, dumps
from logging import getLogger
from socket import socket, SHUT_RDWR


logger = getLogger(__name__)


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
        self.write_stream.write(
            dumps(
                [method, *args],
                **(dumps_kw if dumps_kw else dict())
            )
        )
        self.write_stream.write('\n')
        self.write_stream.flush()
        return loads(self.read_stream.readline(), **(loads_kw if loads_kw else dict()))


def method(id_):
    return partialmethod(SocketRPCClient.remote_procedure_call, id_)


