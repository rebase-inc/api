from multiprocessing import current_process
from rq import Worker, Queue, Connection

from ..app import basic_app
from ..common.settings import config
from ..github.crawl.jobs import create_personal_access_token
from ..features.rq import get_connection, parallel_queues
from ..common.log import setup


conn = get_connection()


logger = setup()


app = basic_app()


create_personal_access_token()


def main():
    with Connection(conn):
        worker = Worker(map(Queue, parallel_queues))
        current_process().name = 'rq_default-'+worker.name[0:5]
        worker.work()


if __name__ == '__main__':
    main()


