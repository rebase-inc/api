from multiprocessing import current_process

from redis import Redis, ConnectionPool
from rq import Worker, Queue, Connection

from ..common.log import setup


def main():
    current_process().name = 'rq_population'
    setup()
    pool = ConnectionPool(host='redis', max_connections=1)
    with Connection(Redis(connection_pool=pool)):
        worker = Worker(map(Queue, ['population']))
        current_process().name = 'rq_population-'+worker.name[0:5]
        worker.work()
        return 0
    return 1


if __name__ == '__main__':
    main()


