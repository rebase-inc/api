from logging import getLogger
from multiprocessing import current_process
from rq import Worker, Queue, Connection

from .app import basic_app
from .features.rq import get_connection, population_queue
from .features.logger import setup_with_conf


conn = get_connection()


app = basic_app()


setup_with_conf(getLogger(), app.config['BASIC_LOG_CONFIG'], app.config['RSYSLOG_CONFIG'])


def main():
    with Connection(conn):
        worker = Worker(map(Queue, [population_queue]))
        current_process().name = 'rq_population-'+worker.name[0:5]
        worker.work()
        return 0
    return 1

if __name__ == '__main__':
    main()


