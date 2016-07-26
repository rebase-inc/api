from builtins import object


class TechnologyScanner(object):

    def scan_contents(self, filename, code, date):
        raise NotImplemented('Abstract method TechnologyScanner.scan_contents')

    def scan_patch(self, filename, code, previous_code, patch, date):
        raise NotImplemented('Abstract method TechnologyScanner.scan_patch')


