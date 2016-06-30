from logging import getLogger
from multiprocessing import current_process
from rq import Worker, Queue, Connection

from rebase.common.config import Config
from rebase.features.rq import get_connection, parallel_queues
from rebase.features.logger import setup_with_conf


conn = get_connection()

setup_with_conf(getLogger(), Config.BASIC_LOG_CONFIG, Config.RSYSLOG_CONFIG)


with Connection(conn):
    worker = Worker(map(Queue, parallel_queues))
    current_process().name = 'rq_default-'+worker.name[0:5]
    worker.work()


