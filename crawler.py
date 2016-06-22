from collections import defaultdict
from logging import getLogger, Formatter
from logging.handlers import SysLogHandler
from multiprocessing import current_process
from pickle import dump
from signal import signal, SIGINT, SIGTERM, SIGQUIT
from sys import exit

from rebase.common.config import Config
from rebase.common.debug import pdebug
from rebase.github import GithubApiRequests, GithubException
from rebase.github.languages import scan_commits


logger = getLogger()
current_process().name = 'crawler'


def quit(signal_number, frame):
    exit()

# from webflow:
rebase_users = [
    'kerseyi',
    'alexpchin',
    'gacpro',
    'Eveykilel',
    'Johnathon332',
    'jitorrent',
    'arunanson',
    'MarkTJBrown',
    'ezynda3',
    'mgraham134',
]

# not a valid user: 'Toahniwalakshay'


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
    github = GithubApiRequests('rebase-dev', 'bf5547c0319871a085b42294d2e2abebf4e08f54')
    pdebug(github.get('/users/rapha-opensource'), 'rapha-opensource')
    all_the_data = defaultdict(dict)
    for user_login in rebase_users:
        try:
            user = github.get('/users/{}'.format(user_login))
        except GithubException as e:
            logger.debug('Error with user {}: %s'.format(user_login), e.message)
            logger.debug('Skipping user')
            continue
        pdebug(user)
        repos = github.get(user['repos_url'])
        commit_count_by_language, unknown_extension_counter, technologies = scan_commits(github, repos, user_login)
        all_the_data[user_login]['commit_count_by_language'] = commit_count_by_language
        all_the_data[user_login]['technologies'] = technologies
        pdebug(all_the_data[user_login])

    github.close()

    with open('/crawler/all_the_data', 'wb') as all_data_file:
        dump(all_the_data, all_data_file)

    logger.debug('Finished crawler')


if __name__ == '__main__':
    main()


