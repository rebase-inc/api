
from .importable_modules import ImportableModules
from .py2_py3_client import Py2Py3Client
from .technology_scanner import TechnologyScanner


class Python(TechnologyScanner):

    def __init__(self):
        super().__init__('Python', Py2Py3Client())

    def context(self, commit):
        return ImportableModules(commit.tree)


