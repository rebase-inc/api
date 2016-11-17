from multiprocessing import current_process
from rq import Worker, Queue, Connection

from ..common.log import setup
from ..common.settings import config
from ..features.rq import get_connection, parallel_queues
from ..github.crawl.jobs import create_personal_access_token


conn = get_connection()


setup()


create_personal_access_token()


def main():
    with Connection(conn):
        worker = Worker(map(Queue, parallel_queues))
        current_process().name = 'rq_default-'+worker.name[0:5]
        worker.work()


if __name__ == '__main__':
    main()


