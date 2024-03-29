from builtins import super


class SubprocessException(Exception):
    msg_fmt = 'SubprocessException'

    def __init__(self, *args):
        self.message = self.msg_fmt.format(*args)

    def __str__(self):
        return self.message


class MessageIsTooBig(SubprocessException):
    msg_fmt = 'Packed message is too big'


class ClosedPipe(SubprocessException):
    msg_fmt = 'process closed pipe: {}'

    def __init__(self, file_name):
        self.file_name = file_name
        super().__init__(file_name)


class ReadingProcessClosedPipe(ClosedPipe):
    msg_fmt = 'Reading '+ClosedPipe.msg_fmt


class WritingProcessClosedPipe(ClosedPipe):
    msg_fmt = 'Writing '+ClosedPipe.msg_fmt


