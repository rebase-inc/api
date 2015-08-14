from os import environ
from urllib.parse import urlparse

from redis import Redis
from rq import Queue


queues = ['high', 'default', 'low']

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
    for q in queues:
        setattr(app, q+'_queue', Queue(name=q, connection=conn))
