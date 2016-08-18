from functools import partialmethod
from json import loads, dumps
from logging import getLogger
from socket import socket, SHUT_RDWR

from rebase.common.debug import pdebug
from rebase.skills.tech_profile import TechProfile
from rebase.skills.technology_scanner import TechnologyScanner


logger = getLogger(__name__)


class Client(TechnologyScanner):

    def __init__(self, host='localhost', port=7777):
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

    def remote_procedure_call(self, method_number, *args):
        self.write_stream.write(dumps([method_number, *args])+'\n')
        self.write_stream.flush()
        return loads(self.read_stream.readline())

    scan_contents = partialmethod(remote_procedure_call, 0)
    scan_patch = partialmethod(remote_procedure_call, 1)
    language = partialmethod(remote_procedure_call, 2)


