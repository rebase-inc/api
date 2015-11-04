from rq import Worker, Queue, Connection

from rebase.features.rq import get_connection, git_queue

conn = get_connection()

with Connection(conn):
    worker = Worker((Queue(git_queue),))
    worker.work()
