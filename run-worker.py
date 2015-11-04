from rq import Worker, Queue, Connection

from rebase.features.rq import get_connection, parallel_queues

conn = get_connection()

with Connection(conn):
    worker = Worker(map(Queue, parallel_queues))
    worker.work()
