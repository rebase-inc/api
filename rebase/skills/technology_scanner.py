from builtins import object
from subprocess import Popen, PIPE


class TechnologyScanner(object):

    def scan_contents(self, filename, code, date):
        raise NotImplemented('Abstract method TechnologyScanner.scan_contents')

    def scan_patch(self, filename, code, previous_code, patch, date):
        raise NotImplemented('Abstract method TechnologyScanner.scan_patch')


class Proxy(TechnologyScanner):

    def __init__(self, executable_path):
        self.process = Popen((executable_path,), stdin=PIPE, stdout=PIPE, stderr=PIPE)

    def scan_patch(self, filename, code, previous_code, patch, date):
        pass

    def scan_contents(self, filename, code, date):
        pass

    def terminate(self):
        self.process.terminate()


