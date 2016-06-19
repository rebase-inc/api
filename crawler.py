from logging import getLogger, Formatter
from logging.handlers import SysLogHandler
from multiprocessing import current_process
from signal import signal, SIGINT, SIGTERM, SIGQUIT
from sys import exit

from requests import get

from rebase.common.config import Config
from rebase.common.debug import pdebug


logger = getLogger()
current_process().name = 'crawler'

class GithubOAuth(object):
    def __init__(self, username, token):
        self.root_url = 'https://api.github.com'
        self.username = username
        self.token = token

    def get(self, path, *args, **kwargs):
        return get(self.root_url+path, *args, auth=(self.username, self.token), **kwargs)


def quit(signal_number, frame):
    exit()


def main():
    signal(SIGINT, quit)
    signal(SIGTERM, quit)
    signal(SIGQUIT, quit)
    conf = Config.BASIC_LOG_CONFIG
    logger.setLevel(conf['level'])
    rsyslog = SysLogHandler(**Config.RSYSLOG_CONFIG)
    rsyslog.setFormatter(Formatter(conf['format']))
    logger.addHandler(rsyslog)
    logger.debug('Started crawler')
    github = GithubOAuth('rapha-opensource', 'ad1e7965dd722d6ae8ec28d5f039112c2ce5a742')
    pdebug(github.get('/users/rapha-opensource').json(), 'rapha-opensource')
    logger.debug('Finished crawler')


if __name__ == '__main__':
    main()
