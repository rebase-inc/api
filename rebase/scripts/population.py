from multiprocessing import current_process
from sys import path
from rq import Worker, Queue, Connection

from ..features.rq import get_connection, population_queue
from ..common.log import setup


conn = get_connection()


setup()


def main():
    with Connection(conn):
        worker = Worker(map(Queue, [population_queue]))
        current_process().name = 'rq_population-'+worker.name[0:5]
        worker.work()
        return 0
    return 1

if __name__ == '__main__':
    main()


