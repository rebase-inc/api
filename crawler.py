from collections import defaultdict
from logging import getLogger, Formatter
from multiprocessing import current_process
from pickle import dump
from signal import signal, SIGINT, SIGTERM, SIGQUIT
from subprocess import check_output
from sys import exit

from rebase.common.debug import pdebug, setup_rsyslog
from rebase.common.stopwatch import InfoElapsedTime
from rebase.github.languages import GithubAccountScanner


logger = getLogger()
current_process().name = 'crawler'


def quit(signal_number, frame):
    exit()

# from webflow:
rebase_users = [
    # famous python devs:
    # Alex Gaynor (PyPy, etc.)
    #'alex',
    # Mike Bayer (SqlAlchemy)
    'zzzeek',
    #'kerseyi',
    #'alexpchin',
    #'gacpro',
    #'Eveykilel',
    #'Johnathon332',
    #'jitorrent',
    #'arunanson',
    #'MarkTJBrown',
    #'ezynda3',
    #'mgraham134',
]

# not a valid user: 'Toahniwalakshay'


def main():
    signal(SIGINT, quit)
    signal(SIGTERM, quit)
    signal(SIGQUIT, quit)
    setup_rsyslog()
    logger.info('Started crawler')
    for user_login in rebase_users:
        user_data = dict()
        start_msg = 'processing Github user: '+user_login
        with InfoElapsedTime(start=start_msg, stop=start_msg+' took %f seconds'):
            commit_count_by_language, unknown_extension_counter, technologies = GithubAccountScanner(
                'bf5547c0319871a085b42294d2e2abebf4e08f54',
                'rebase-dev'
            ).scan_all_repos(login=user_login)
            user_data['commit_count_by_language'] = commit_count_by_language
            user_data['technologies'] = technologies
            user_data['unknown_extension_counter'] = unknown_extension_counter
            with open('/crawler/{}/data'.format(user_login), 'w') as f:
                dump(user_data, f)
    logger.info('Finished crawling')
    exit()


if __name__ == '__main__':
    main()


