from json import loads, dumps
from logging import getLogger
from socket import socket, SHUT_RDWR

from rebase.common.debug import pdebug
from rebase.skills.tech_profile import TechProfile
from rebase.skills.technology_scanner import TechnologyScanner


logger = getLogger(__name__)


LANGUAGE_PREFIX = 'Python.'


class JavascriptScanner(TechnologyScanner):

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

    def scan_contents(self, filename, code, date):
        self.write_stream.write(dumps([0, filename, code, date])+'\n')
        self.write_stream.flush()
        return loads(self.read_stream.readline())

    def scan_patch(self, filename, code, previous_code, patch, date):
        self.write_stream.write(dumps([0, filename, code, previous_code, date])+'\n')
        self.write_stream.flush()
        return load(self.read_stream)


