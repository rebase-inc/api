from abc import ABCMeta, abstractmethod
from logging import getLogger

from .scanner_client import ScannerClient
from .tech_profile import TechProfile, Exposure


logger = getLogger(__name__)


class TechnologyScanner:
    '''

        A client to talk to a scanner that supports only one language

    '''

    __metaclass__ = ABCMeta

    def __init__(self, language, scanner_client):
        assert isinstance(scanner_client, ScannerClient)
        self.client = scanner_client
        self.languages = self.client.languages()
        if language not in self.languages:
            raise ValueError('Language "{}" is not supported'.format(language))
        self.language = language
        self.language_index = self.languages.index(self.language)
        self.grammar = self.client.grammar(self.language_index)

    def scan_contents(self, filename, code, date, commit):
        '''
            Return a TechProfile object for 'code'
        '''
        use = self.client.scan_contents(
            self.language_index,
            filename,
            code,
            self.context(commit)
        )
        return TechProfile({ self.language+'.'+rule: Exposure(date, date, reps) for rule, reps in use.items() })

    def scan_diff(
        self,
        filename,
        code,
        commit,
        parent_code,
        parent_commit,
        date
    ):
        '''
            Return a TechProfile object for the modified 'code'
        '''
        before = self.client.scan_contents(
            self.language_index,
            filename,
            parent_code,
            self.context(parent_commit)
        )
        after = self.client.scan_contents(
            self.language_index,
            filename,
            code,
            self.context(commit)
        )
        profile = TechProfile()
        all_technologies = set(before.keys()) | set(after.keys())
        for technology in all_technologies:
            in_before = technology in before
            in_after = technology in after
            if in_before and in_after:
                abs_diff = abs(before[technology] - after[technology])
                if abs_diff > 0:
                    profile.add(self.language+'.'+technology, date, abs_diff)
            elif in_before and not in_after:
                profile.add(self.language+'.'+technology, date, before[technology])
            elif not in_before and in_after:
                profile.add(self.language+'.'+technology, date, after[technology])
        return profile


    @abstractmethod
    def context(self, commit):
        '''
        Extract an object with additional information to be passed to the scan_* functions.
        For example a tree of package directories to help parse the libraries import paths.
        This is obviously language and project specific.
        Defaults to returning None.
        '''
        pass

    def close(self):
        self.client.close()


