from multiprocessing import current_process
from rq import Worker, Queue, Connection

from redis import StrictRedis

from ..common.settings import config
from ..common.log import setup
from ..github.crawl.jobs import create_personal_access_token


current_process().name = config['SERVICE_NAME']


def main():
    setup()
    with Connection(StrictRedis('redis')):
        worker = Worker(map(Queue, config['QUEUES']))
        current_process().name = config['SERVICE_NAME']+'.'+worker.name[0:5]
        create_personal_access_token()
        worker.work(logging_level=config['LOG_LEVEL'])


if __name__ == '__main__':
    main()


