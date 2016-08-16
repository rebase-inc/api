from logging import getLogger
from multiprocessing import current_process
from rq import Worker, Queue, Connection

from rebase.app import basic_app
from rebase.github.crawl.jobs import create_personal_access_token
from rebase.features.rq import get_connection, parallel_queues
from rebase.features.logger import setup_with_conf


conn = get_connection()


app = basic_app()

setup_with_conf(getLogger(), app.config['BASIC_LOG_CONFIG'], app.config['RSYSLOG_CONFIG'])


create_personal_access_token(app)


with Connection(conn):
    worker = Worker(map(Queue, parallel_queues))
    current_process().name = 'rq_default-'+worker.name[0:5]
    worker.work()


