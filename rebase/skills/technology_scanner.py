from builtins import object

from rebase.skills.tech_profile import TechProfile


class TechnologyScanner(object):

    def scan_contents(self, filename, code, date, context):
        '''
            Return a TechProfile object for 'code'
        '''
        raise NotImplemented('TechnologyScanner.scan_contents')

    def scan_patch(self, filename, code, previous_code, patch, date, context):
        '''
            Return a TechProfile object for the modified 'code'
        '''
        raise NotImplemented('TechnologyScanner.scan_contents')

    def context(self, commit, parent_commit=None):
        '''
        Extract a dictionary of additional information to be passed to the scan_* functions.
        For example a tree of package directories to help parse the libraries import paths.
        This is obviously language and project specific.
        Defaults to returning None.
        '''
        return None


