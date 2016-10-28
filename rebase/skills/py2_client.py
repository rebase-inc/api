from .proxy_scanner import Proxy


class Py2Client(Proxy):

    def __init__(self):
        super().__init__('/api/parse_python2.py', '/tmp')


