from rq import Worker, Queue, Connection

from rebase.features.rq import get_connection, queues

conn = get_connection()

with Connection(conn):
    worker = Worker(map(Queue, queues))
    worker.work()
