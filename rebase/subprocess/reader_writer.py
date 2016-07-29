from builtins import object
from logging import getLogger, INFO
from select import poll, POLLIN, POLLPRI, POLLOUT, POLLHUP, POLLERR, POLLNVAL
from struct import pack, unpack

from .exceptions import MessageIsTooBig, ReadingProcessClosedPipe, WritingProcessClosedPipe


logger = getLogger(__name__)
logger.setLevel(INFO)


def log_event(event):
    logger.debug('POLLIN[%r]', bool(event & POLLIN))
    logger.debug('POLLPRI[%r]', bool(event & POLLPRI))
    logger.debug('POLLOUT[%r]', bool(event & POLLOUT))
    logger.debug('POLLHUP[%r]', bool(event & POLLHUP))
    logger.debug('POLLERR[%r]', bool(event & POLLERR))
    logger.debug('POLLNVAL[%r]', bool(event & POLLNVAL))


def write(file_, object_, packb, max_len, fmt):
    poll_ = poll()
    fd = file_.fileno()
    poll_.register(fd, POLLOUT|POLLHUP|POLLERR|POLLNVAL)
    packed_object = packb(object_)
    length = len(packed_object)
    if (length.bit_length() // 8) > max_len:
        raise MessageIsTooBig()
    packed_length = pack(fmt, length)
    data = packed_length+packed_object
    logger.debug('Waiting for WRITE access to %s', file_.name)
    fd_, event = poll_.poll()[0]
    assert fd_ == fd
    log_event(event)
    if not bool(event & POLLOUT) and bool(event & POLLHUP):
        raise ReadingProcessClosedPipe(file_.name)
    file_.write(data)
    file_.flush()
    poll_.unregister(fd)


def read(file_, unpackb, max_len, fmt):
    '''
        Reads the next object from the file_
    '''
    poll_ = poll()
    fd = file_.fileno()
    poll_.register(fd, POLLIN|POLLPRI|POLLHUP|POLLERR|POLLNVAL)
    remaining = max_len
    packed_length = b''
    while True:
        logger.debug('Waiting for READ access to %s', file_.name)
        fd_, event = poll_.poll()[0]
        assert fd == fd_
        log_event(event)
        if not bool(event & POLLIN) and bool(event & POLLHUP):
            raise WritingProcessClosedPipe(file_.name)
        received = file_.read(remaining)
        remaining -= len(received)
        packed_length += received
        logger.debug('received: %d bytes', len(received))
        if not remaining:
            break
    length = unpack(fmt, packed_length)[0]
    logger.debug('reading %d bytes for packed_object', length)
    packed_object = b''
    remaining = length
    while True:
        received = file_.read(remaining)
        remaining -= len(received)
        packed_object += received
        logger.debug('received %d bytes', len(received))
        if not remaining:
            break
        else:
            logger.debug('Waiting for READ access to %s', file_.name)
            fd_, event = poll_.poll()[0]
            assert fd == fd_
            log_event(event)
            if not bool(event & POLLIN) and bool(event & POLLHUP):
                raise WritingProcessClosedPipe(file_.name)
    logger.debug('packed_object: %s', packed_object)
    poll_.unregister(fd)
    return unpackb(packed_object)


class ReaderWriter(object):

    def __init__(self,
                 packed_object_max_length,
                 object_length_format,
                 packb,
                 unpackb
                 ):
        self.packed_objet_max_length = 4 # bytes
        self.object_length_format = '!L' # big-endian 4 bytes unsigned long
        self.packb = packb
        self.unpackb = unpackb

    def read(self, file_):
        return read(file_, self.unpackb, self.packed_objet_max_length, self.object_length_format)

    def write(self, file_, object_):
        return write(file_, object_, self.packb, self.packed_objet_max_length, self.object_length_format)


