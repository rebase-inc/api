from logging import getLogger
from multiprocessing import current_process
from rq import Worker, Queue, Connection

from redis import Redis

from ..common.log import setup
from ..common.settings import config
from ..features.rq import git_queue
from ..git.keys import generate_authorized_keys
from ..git.users import generate_authorized_users_for_all_projects




generate_authorized_keys()


generate_authorized_users_for_all_projects()


with Connection(Redis('redis')):
    current_process().name = 'rq_git'
    setup()
    worker = Worker((Queue(git_queue),))
    current_process().name = 'rq_git.'+worker.name[0:5]
    worker.work(logging_level=config['LOG_LEVEL'])


