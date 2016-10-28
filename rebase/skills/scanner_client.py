from abc import ABCMeta, abstractmethod
from functools import partial
from logging import getLogger


logger = getLogger(__name__)


class ScannerClient:
    '''
        A client to talk to a scanner that supports multiple languages.
    '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def languages(self):
        '''
        Concrete implementations should return a tuple of ( <language>, ... )
        where <language> is a string containing a language.
        '''
        pass

    @abstractmethod
    def grammar(self, language_index):
        '''
        Returns the tuple of grammar constructs available with the language identified by its index.
        'language_index' is the position of the language to be used in the tuple returned by the 'languages' method.
        '''
        pass

    def close(self):
        pass

    @abstractmethod
    def scan_contents(self, language_index, filename, code, context):
        '''
            Returns a dictionary of technology to use count.
            'language_index' is the position of the language to be used in the tuple returned by the 'languages' method.

        '''
        pass


