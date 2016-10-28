from logging import getLogger
from subprocess import Popen, PIPE

from .py2_client import Py2Client
from .python_client import PythonClient


logger = getLogger(__name__)


class Py2Py3Client(PythonClient):

    def __init__(self):
        self.use_py2 = False
        self.py2 = Py2Client()
        super().__init__()

    def switch_py_version_on_syntax_error(self, py2_method, py3_method, *args):
        if self.use_py2:
            try:
                return py2_method(*args)
            except SyntaxError as e:
                logger.warning('Detected SyntaxError: %s', e)
                logger.warning('Switching to Python 3')
                self.use_py2 = False
                return py3_method(*args)
        else:
            try:
                return py3_method(*args)
            except SyntaxError as e:
                logger.warning('Detected SyntaxError: %s', e)
                logger.warning('Switching to Python 2')
                self.use_py2 = True
                return py2_method(*args)

    def scan_contents(self, *args):
        return self.switch_py_version_on_syntax_error(self.py2.scan_contents, super().scan_contents, *args)

    def close(self):
        self.py2.close()

