from builtins import bytes, super
from functools import partial
from json import loads, dumps
from logging import getLogger

from .reader_writer import ReaderWriter
from .transport import ServerTransport, ClientSubprocess


logger = getLogger(__name__)


def packb(object_, **kwargs):
    return bytes(dumps(object_, **kwargs), 'utf-8')


def unpackb(bytes_, **kwargs):
    return loads(bytes(bytes_).decode(), **kwargs)


class JsonReaderWriter(ReaderWriter):
    
    def __init__(self, dumps_kwargs=dict(), loads_kwargs=dict()):
        # 4 bytes => 1GB is max size of serialized objects
        # '!' means big-ending
        # L means 4 bytes unsigned long (see python doc)
        super().__init__(4, '!L', partial(packb, **dumps_kwargs), partial(unpackb, **loads_kwargs))


class JsonServerSubprocess(ServerTransport):
    
    def __init__(self, fifo_dir, dumps_kwargs=dict(), loads_kwargs=dict()):
        super().__init__(fifo_dir, JsonReaderWriter(dumps_kwargs, loads_kwargs))


class JsonClientSubprocess(ClientSubprocess):

    def __init__(self, exec_args, fifo_dir, dumps_kwargs=dict(), loads_kwargs=dict()):
        super().__init__(exec_args, fifo_dir, JsonReaderWriter(dumps_kwargs, loads_kwargs))


