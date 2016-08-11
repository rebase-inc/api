from builtins import object


class TechnologyScanner(object):

    def scan_contents(self, filename, code, date):
        '''
            Return a TechProfile object for 'code'
        '''
        raise NotImplemented('Abstract method TechnologyScanner.scan_contents')

    def scan_patch(self, filename, code, previous_code, patch, date):
        '''
            Return a TechProfile object for the modified 'code'
        '''
        raise NotImplemented('Abstract method TechnologyScanner.scan_patch')


