from os import environ
from urllib.parse import urlparse

from redis import Redis
from rq import Queue

git_queue = 'git'

# Parallel queues support multiple workers pulling tasks from the same queue
# Serial queues are guaranteed to have only one worker per queue.

parallel_queues = ['high', 'default', 'low']
serial_queues = [git_queue]
all_queues = parallel_queues+serial_queues

def get_connection():
    redis_url = environ.get('REDIS_URL', '')
    if not redis_url:
        conn = Redis()
    else:
        url = urlparse(redis_url)
        conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)
    return conn

def setup_rq(app):
    conn = get_connection()
    for q in all_queues:
        setattr(app, q+'_queue', Queue(name=q, connection=conn))
