from .proxy_scanner import Proxy


class Py2Client(Proxy):

    def __init__(self):
        super().__init__(('/venv/rq_p2/bin/python', '-m', 'rebase.scripts.parse_python2'), '/tmp')


