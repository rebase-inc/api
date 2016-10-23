from builtins import object, super
from functools import partial
from os import mkfifo, unlink
from os.path import exists, join
from subprocess import Popen
from sys import exit, stdin, stdout, stderr


class Transport(object):
    '''
        This is similar to Python 3's asyncio Transport.
        Basically, it abstracts out all the byte level implementation details
        of how data gets transported between protocol calls.
    '''

    def close(self):
        raise NotImplemented('Abstract close')

    def pipes_from_dir(self, fifo_dir):
        return tuple(map(lambda pipe: join(fifo_dir, pipe), ('in', 'out', 'err')))


class ServerTransport(Transport):

    def __init__(self, fifo_dir, reader_writer):
        pipes_ = self.pipes_from_dir(fifo_dir)
        self.reader_writer = reader_writer
        self.in_ = open(pipes_[0], 'rb')
        self.out = open(pipes_[1], 'wb')
        self.err = open(pipes_[2], 'wb')

    def read_in(self):
        return self.reader_writer.read(self.in_)

    def write_out(self, object_):
        return self.reader_writer.write(self.out, object_)

    def write_err(self, object_):
        return self.reader_writer.write(self.err, object_)

    def close(self):
        self.in_.close()
        self.out.close()
        self.err.close()


class ClientTransport(Transport):

    def __init__(self, fifo_dir, reader_writer):
        self.reader_writer = reader_writer
        self.pipes = self.pipes_from_dir(fifo_dir)
        for pipe in self.pipes:
            if exists(pipe):
                unlink(pipe)
            mkfifo(pipe)
        self.in_ = None
        self.out = None
        self.err = None

    def open(self):
        self.in_ = open(self.pipes[0], 'wb')
        self.out = open(self.pipes[1], 'rb')
        self.err = open(self.pipes[2], 'rb')

    def write_in(self, object_):
        return self.reader_writer.write(self.in_, object_)

    def read_err(self):
        return self.reader_writer.read(self.err)

    def read_out(self):
        return self.reader_writer.read(self.out)

    def close(self):
        self.in_.close()
        self.out.close()
        self.err.close()


class ClientSubprocess(ClientTransport):

    def __init__(self, exec_path, fifo_dir, reader_writer):
        super().__init__(fifo_dir, reader_writer)
        self.subprocess = Popen((exec_path, fifo_dir))
        super().open()

    def close(self):
        super().close()
        self.subprocess.terminate()


