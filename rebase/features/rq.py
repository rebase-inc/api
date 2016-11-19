from os import environ
from urllib.parse import urlparse

from redis import Redis
from rq import Queue

git_queue = 'git'

population_queue = 'population'

# Parallel queues support multiple workers pulling tasks from the same queue
# Serial queues are guaranteed to have only one worker per queue.

parallel_queues = ['high', 'default', 'low']
serial_queues = [git_queue, population_queue]
all_queues = parallel_queues+serial_queues

def get_connection():
    return Redis(host='redis')

def setup_rq(any_object):
    conn = get_connection()
    for q in all_queues:
        setattr(any_object, q+'_queue', Queue(name=q, connection=conn))


class Queues(object): pass

ALL_QUEUES = Queues()


setup_rq(ALL_QUEUES)


POPULATION = ALL_QUEUES.population_queue

DEFAULT = ALL_QUEUES.default_queue


