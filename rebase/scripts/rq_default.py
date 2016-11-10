from logging import getLogger
from multiprocessing import current_process
from rq import Worker, Queue, Connection

from rebase.app import basic_app
from rebase.common.settings import config
from rebase.github.crawl.jobs import create_personal_access_token
from rebase.features.rq import get_connection, parallel_queues
from rebase.features.logger import setup


conn = get_connection()


setup(getLogger(), config['LOG_LEVEL'], config['RSYSLOG_CONFIG']['address'], config['LOG_FORMAT'])


app = basic_app()


create_personal_access_token()


def main():
    with Connection(conn):
        worker = Worker(map(Queue, parallel_queues))
        current_process().name = 'rq_default-'+worker.name[0:5]
        worker.work()


if __name__ == '__main__':
    main()


