from logging import getLogger
from multiprocessing import current_process
from rq import Worker, Queue, Connection

from rebase.app import basic_app
from rebase.features.logger import setup_with_conf
from rebase.features.rq import get_connection, git_queue
from rebase.git.keys import generate_authorized_keys
from rebase.git.users import generate_authorized_users_for_all_projects


current_process().name = 'rq_git'


app = basic_app()


setup_with_conf(getLogger(), app.config['BASIC_LOG_CONFIG'], app.config['RSYSLOG_CONFIG'])


generate_authorized_keys()


generate_authorized_users_for_all_projects()


conn = get_connection()


with Connection(conn):
    worker = Worker((Queue(git_queue),))
    worker.work()


