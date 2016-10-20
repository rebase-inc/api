from logging import getLogger
from subprocess import Popen, PIPE

from .proxy_scanner import Proxy
from .python import PythonScanner


logger = getLogger(__name__)


class Py2Scanner(Proxy):

    def __init__(self):
        super().__init__('/api/parse_python2.py', '/tmp')


class Py2Py3Scanner(PythonScanner):

    def __init__(self):
        self.use_py2 = False
        self.py2 = Py2Scanner()

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

    def scan_patch(self, *args):
        return self.switch_py_version_on_syntax_error(self.py2.scan_patch, super().scan_patch, *args)

    def scan_contents(self, *args):
        return self.switch_py_version_on_syntax_error(self.py2.scan_contents, super().scan_contents, *args)

    def close(self):
        self.py2.close()

