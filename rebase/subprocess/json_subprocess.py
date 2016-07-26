from builtins import bytes, super
from json import loads, dumps
from logging import getLogger

from .reader_writer import ReaderWriter
from .transport import ServerTransport, ClientSubprocess


logger = getLogger(__name__)


def packb(object_):
    return bytes(dumps(object_), 'utf-8')


def unpackb(bytes_):
    return loads(bytes(bytes_).decode())


class JsonReaderWriter(ReaderWriter):
    
    def __init__(self):
        # 4 bytes => 1GB is max size of serialized objects
        # '!' means big-ending
        # L means 4 bytes unsigned long (see python doc)
        super().__init__(4, '!L', packb, unpackb)


class JsonServerSubprocess(ServerTransport):
    
    def __init__(self, fifo_dir):
        super().__init__(fifo_dir, JsonReaderWriter())


class JsonClientSubprocess(ClientSubprocess):

    def __init__(self, exec_path, fifo_dir):
        super().__init__(exec_path, fifo_dir, JsonReaderWriter())


