from .reader_writer import ReaderWriter


class MsgpackReaderWriter(ReaderWriter):
    
    def __init__(self):
        from msgpack import packb, unpackb
        super().__init__(4, '!L', packb, unpackb)



