
from redis import StrictRedis
from rq import Queue


all_queue_names = [
    'population',
    'default',
    'github_public_crawling',
]


def queue(app, q):
    return Queue(name=q, connection=StrictRedis(connection_pool=app.redis_pool))


