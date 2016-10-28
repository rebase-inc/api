
from .remote_scanner_client import RemoteScannerClient
from .technology_scanner import TechnologyScanner


class Javascript(TechnologyScanner):

    def __init__(self):
        super().__init__('Javascript', RemoteScannerClient('javascript', 7777))

    def context(self, commit):
        if commit:
            return commit.binsha
        else:
            return None


