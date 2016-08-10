from logging import getLogger
from multiprocessing import current_process
from signal import signal, SIGINT, SIGTERM, SIGQUIT
from sys import exit
from time import sleep

from redis import StrictRedis

from rebase.common.dev import CRAWLER_PUBLIC_REPOS_TOKENS
from rebase.common.debug import setup_rsyslog
from rebase.crawl.jobs import scan_user
from rebase.features.rq import setup_rq


logger = getLogger()


current_process().name = 'crawler'


def quit(signal_number, frame):
    exit()

# from webflow:
rebase_users = [
    # famous python devs:
    # Alex Gaynor (PyPy, etc.)
    'alex',
    # Mike Bayer (SqlAlchemy)
    'zzzeek',
    'rapha-opensource',
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

class Queues(object): pass


def main():
    signal(SIGINT, quit)
    signal(SIGTERM, quit)
    signal(SIGQUIT, quit)
    setup_rsyslog()
    logger.info('Started crawler')
    # load Github Personal Tokens
    token_list = 'crawler_github_tokens'
    redis = StrictRedis(host='redis')
    redis.delete(token_list)
    redis.lpush(token_list, *CRAWLER_PUBLIC_REPOS_TOKENS.values())
    all_queues = Queues()
    setup_rq(all_queues)
    rq_default = all_queues.default_queue
    all_jobs = [ rq_default.enqueue_call(func=scan_user, args=(user_login, token_list), timeout=7200) for user_login in rebase_users ]
    jobs = all_jobs
    while True:
        sleep(60)
        remaining_jobs = tuple(filter(lambda job: not (job.is_finished or job.is_failed), jobs))
        logger.info('Crawling is %d%% complete', 100*((len(all_jobs) - len(remaining_jobs))//len(all_jobs)))
        jobs = remaining_jobs
        if not jobs:
            break
    redis.delete(token_list)
    logger.info('Finished crawling')
    exit()


if __name__ == '__main__':
    main()


